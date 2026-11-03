pipeline {
    agent any

    environment {
        APP_IMAGE     = 'flask-vulnerable'
        APP_CONTAINER = 'flask-vulnerable-app'
        ZAP_IMAGE     = 'ghcr.io/zaproxy/zaproxy:stable'
        ZAP_TARGET    = 'http://flask-vulnerable-app:5000/hello?name=test'
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
                              -Dsonar.exclusions=deps/**,**/*.html,**/*.xml,**/*.json \
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
                // 1) OWASP Dependency-Check: dependencias del proyecto
                sh '''
                    rm -rf deps && mkdir deps
                    docker rm -f deps-extract || true
                    docker create --name deps-extract $APP_IMAGE:latest
                    docker cp deps-extract:/usr/local/lib/python3.11/site-packages ./deps
                    docker rm deps-extract
                '''
                withCredentials([string(credentialsId: 'nvd_api_key', variable: 'NVD_API_KEY')]) {
                    dependencyCheck odcInstallation: 'DC',
                        additionalArguments: "--scan ./ --out ./ --format HTML --format XML --enableExperimental --disableOssIndex --disableAssembly --nvdApiKey ${env.NVD_API_KEY}"
                }
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'

                // 2) OWASP ZAP: análisis dinámico sobre la app desplegada
                sh '''
                    docker rm -f zap-scan || true
                    docker run --name zap-scan -u root --network devsecops -v /zap/wrk $ZAP_IMAGE \
                        zap-full-scan.py -t "$ZAP_TARGET" -r zap-report.html -m 1 -I || true
                    docker cp zap-scan:/zap/wrk/zap-report.html ./zap-report.html
                    docker rm -f zap-scan
                '''
                publishHTML(target: [
                    reportDir: '.',
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])

                archiveArtifacts artifacts: 'dependency-check-report.html, zap-report.html', allowEmptyArchive: true
            }
        }
    }
}