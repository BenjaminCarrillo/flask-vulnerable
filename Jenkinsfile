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
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=flask-vulnerable \
                              -Dsonar.projectName=flask-vulnerable \
                              -Dsonar.sources=. \
                              -Dsonar.exclusions=**/*.html,**/*.xml,**/*.json \
                              -Dsonar.python.version=3.11
                        """
                    }
                }
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
                withCredentials([string(credentialsId: 'nvd-api-key', variable: 'NVD_API_KEY')]) {
                    dependencyCheck odcInstallation: 'DC',
                        additionalArguments: "--scan ./ --out ./ --format HTML --format XML --enableExperimental --disableOssIndex --nvdApiKey ${env.NVD_API_KEY}"
                }
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'

                echo 'OWASP ZAP: se agrega en el Paso 5'
            }
        }
    }
}