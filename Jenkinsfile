pipeline {
  agent any
  environment {
  VERSION = """${sh(
              returnStdout: true,
              script: 'cat VERSION'
            )}"""
  }

  stages {
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
          git add -A
          git commit -m 'init'
          git push origin master
        '''
      }
    }
  }
}






    


    

    