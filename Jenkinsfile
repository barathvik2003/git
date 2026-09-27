pipeline {

    agent any

    environment {
        APP_NAME = 'company-management'
        REGISTRY = 'localhost:5000'
        IMAGE = "${REGISTRY}/${APP_NAME}"
        PORT = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    ./venv/bin/pip install pytest
                    ./venv/bin/pytest -v
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    ./venv/bin/pip install pip-audit
                    ./venv/bin/pip-audit -r requirements.txt || true
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    podman build \
                    -t ${IMAGE}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    podman push \
                    ${IMAGE}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    podman rm -f ${APP_NAME} || true

                    podman run -d \
                      --name ${APP_NAME} \
                      -p ${PORT}:5000 \
                      ${IMAGE}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 5

                    curl --fail \
                    http://localhost:${PORT}/health
                '''
            }
        }
    }

    post {

        success {
            echo "Deployment successful"
        }

        failure {
            echo "Pipeline failed"
        }
    }
}
