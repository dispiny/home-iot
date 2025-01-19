// pipeline {
//   agent any
//   environment {
//   VERSION = """${sh(
//               returnStdout: true,
//               script: 'cat VERSION'
//             )}"""
//   }

//   stages {
//     stage('Pre-Build') {
//       steps {
//         echo "VERSION: $VERSION"
//       }
//     }

//     stage('Build') {
//       steps {
//         sh '''#!/bin/bash
//           docker build -t ghcr.io/dispiny/home-iot:v$VERSION ./
//         '''
//       }
//     }

//     stage('Post-Build') {
//       steps {
//         withCredentials(bindings: [usernamePassword(credentialsId: 'd36dc810-948b-4fc2-976a-558fe517ab6d', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
//           sh """
//             echo $VERSION
//             echo $GIT_PASSWORD | docker login ghcr.io -u $GIT_USERNAME --password-stdin
//             docker push ghcr.io/dispiny/home-iot:v$VERSION
//           """
//         }
//         echo "VERSION: $VERSION"
//         sh '''#!/bin/bash
//           docker rmi $(docker images -q)
//         '''
//       }
//     }

//     stage('helm-Pre-Build') {
//       steps {
//         sh '''#!/bin/bash
//         echo $VERSION
//         sed -i "s|version:.*|version: $VERSION|g" helm/Chart.yaml
//         sed -i "s|tag:.*|tag: v$VERSION|g" helm/values.yaml
//         '''
//       }
//     }

//     stage('helm-Build') {
//       steps {
//         sh '''#!/bin/bash
//           helm package helm --destination helm/
//           helm repo index . --merge index.yaml --url https://github.com/dispiny/home-iot/releases/download/v$VERSION/
//           '''
//       }
//     }

//   stage('helm-Post-Build') {
//       steps {
//         sh '''
//           git config user.name "dispiny"
//           git config user.email "aws.pjm1024cl@gmail.com"
//         '''
//         withCredentials(bindings: [usernamePassword(credentialsId: 'd36dc810-948b-4fc2-976a-558fe517ab6d', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
//           sh """
//                       git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/dispiny/home-iot.git
//                       echo $GIT_PASSWORD | gh auth login --with-token 
//                     """
//         }

//         sh '''
//           NAME=$(gh release view v$VERSION --json assets --jq \'.assets[].name\' || echo nope)
//           isFiles=$(echo $NAME | grep tgz | wc -l)
//           echo $isFiles
//           if [ $isFiles -eq 0 ]; then
//             gh release create v$VERSION ./helm/home-iot-$VERSION.tgz -t v$VERSION --generate-notes
//           elif [ $isFiles -eq 1 ]; then
//             gh release delete v$VERSION -y
//             gh release create v$VERSION ./helm/home-iot-$VERSION.tgz -t v$VERSION --generate-notes
//           fi

//           rm -rf helm/*.tgz
//           sed -i 's|helm/||g' index.yaml

//           git checkout helm || git checkout -b helm

//           git add index.yaml
//           git commit -m "Update(index.yaml): Version Up -> v$VERSION"
//           git push origin helm
//         '''
//       }
//     }
//   }
// }






    


    

pipeline {
  agent any
  environment {
    VERSION = """${sh(
                returnStdout: true,
                script: 'cat VERSION'
              )}"""
  }

  stages {
    stage('Check Changes') {
      steps {
        script {
          // 변경된 파일 목록 가져오기
          def changedFiles = sh(
            script: 'git diff --name-only HEAD HEAD~1',
            returnStdout: true
          ).trim().split('\n')

          // index.yaml만 수정되었는지 확인
          def onlyIndexYamlChanged = changedFiles.size() == 1 && changedFiles[0] == "index.yaml"

          if (onlyIndexYamlChanged) {
            echo "Only index.yaml was modified. Skipping build."
            currentBuild.result = 'SUCCESS' // 빌드를 성공 상태로 종료
            error("Skipping further stages.") // 이후 단계를 실행하지 않음
          } else {
            echo "Changes detected in files other than index.yaml. Proceeding with build."
          }
        }
      }
    }

    stage('Pre-Build') {
      steps {
        echo "VERSION: $VERSION"
      }
    }

    stage('Build') {
      steps {
        sh '''#!/bin/bash
          docker build -t ghcr.io/dispiny/home-iot:v$VERSION ./
        '''
      }
    }

    stage('Post-Build') {
      steps {
        withCredentials(bindings: [usernamePassword(credentialsId: 'd36dc810-948b-4fc2-976a-558fe517ab6d', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
          sh """
            echo $VERSION
            echo $GIT_PASSWORD | docker login ghcr.io -u $GIT_USERNAME --password-stdin
            docker push ghcr.io/dispiny/home-iot:v$VERSION
          """
        }
        echo "VERSION: $VERSION"
        sh '''#!/bin/bash
          docker rmi $(docker images -q)
        '''
      }
    }

    stage('helm-Pre-Build') {
      steps {
        sh '''#!/bin/bash
        echo $VERSION
        sed -i "s|version:.*|version: $VERSION|g" helm/Chart.yaml
        sed -i "s|tag:.*|tag: v$VERSION|g" helm/values.yaml
        '''
      }
    }

    stage('helm-Build') {
      steps {
        sh '''#!/bin/bash
          helm package helm --destination helm/
          helm repo index . --merge index.yaml --url https://github.com/dispiny/home-iot/releases/download/v$VERSION/
          '''
      }
    }

    stage('helm-Post-Build') {
      steps {
        sh '''
          git config user.name "dispiny"
          git config user.email "aws.pjm1024cl@gmail.com"
        '''
        withCredentials(bindings: [usernamePassword(credentialsId: 'd36dc810-948b-4fc2-976a-558fe517ab6d', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
          sh """
                      git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/dispiny/home-iot.git
                      echo $GIT_PASSWORD | gh auth login --with-token 
                    """
        }

        sh '''
          NAME=$(gh release view v$VERSION --json assets --jq \'.assets[].name\' || echo nope)
          isFiles=$(echo $NAME | grep tgz | wc -l)
          echo $isFiles
          if [ $isFiles -eq 0 ]; then
            gh release create v$VERSION ./helm/home-iot-$VERSION.tgz -t v$VERSION --generate-notes
          elif [ $isFiles -eq 1 ]; then
            gh release delete v$VERSION -y
            gh release create v$VERSION ./helm/home-iot-$VERSION.tgz -t v$VERSION --generate-notes
          fi

          rm -rf helm/*.tgz
          sed -i 's|helm/||g' index.yaml

          git add index.yaml
          git commit -m "Update(index.yaml): Version Up -> v$VERSION"
          git push origin helm
        '''
      }
    }
  }
}
