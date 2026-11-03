pipeline {
    agent any

    environment {
        APP_IMAGE     = 'flask-vulnerable'
        APP_CONTAINER = 'flask-vulnerable-app'
    }

    stages {
        stage('Build') {
            steps {
                sh 'docker build -t $APP_IMAGE:latest .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run --rm $APP_IMAGE:latest python -m unittest -v'
            }
        }
        stage('Analyze') {
            steps {
                echo 'SonarQube: se configura en el Paso 4'
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f $APP_CONTAINER || true
                    docker run -d --name $APP_CONTAINER --network devsecops -p 5000:5000 $APP_IMAGE:latest
                '''
            }
        }
        stage('Security Test') {
            steps {
                dependencyCheck odcInstallation: 'DC',
                    additionalArguments: '--scan ./ --out ./ --format HTML --format XML --enableExperimental --disableOssIndex'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'

                echo 'OWASP ZAP: se agrega en el Paso 5'
            }
        }
    }
}