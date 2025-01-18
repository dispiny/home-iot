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
        withCredentials(bindings: [usernamePassword(credentialsId: 'd36dc810-948b-4fc2-976a-558fe517ab6d', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
          sh """
            echo $GIT_PASSWORD | docker login ghcr.io -u dispiny --password-stdin
          """
        }
      }
    }

    stage('Build') {
      steps {
        sh '''#!/bin/bash
          docker build -t ghcr.io/dispiny/home-iot:v$VERSION . 
        '''
      }
    }

    stage('Post-Build') {
      steps {
        sh 'echo $VERSION'
        sh 'docker push ghcr.io/dispiny/home-iot:v$VERSION'
        sh '''#!/bin/bash
rm -rf *
rm -rf .*'''
      }
    }
  }
}