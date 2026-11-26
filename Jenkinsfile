pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE = 'devops-app'
        TAG   = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build image') {
            steps {
                sh 'docker build --provenance=false --build-arg APP_VERSION=${TAG} -t ${IMAGE}:${TAG} .'
            }
        }

        stage('Tests') {
            steps {
                sh 'docker run --rm -v "$PWD/test_app.py:/app/test_app.py" ${IMAGE}:${TAG} python -m pytest -q /app/test_app.py'
            }
        }

        stage('Load into Minikube') {
            steps {
                sh 'sudo -u vagrant -H /usr/local/bin/minikube image load ${IMAGE}:${TAG}'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    sed "s|image: devops-app:local|image: ${IMAGE}:${TAG}|" k8s/deployment.yaml \
                        | sudo -u vagrant -H /snap/bin/kubectl apply -f -
                    sudo -u vagrant -H /snap/bin/kubectl apply -f - < k8s/service.yaml
                    sudo -u vagrant -H /snap/bin/kubectl rollout status deployment/devops-app --timeout=180s
                '''
            }
        }
    }

    post {
        success { echo "Deploiement reussi : ${IMAGE}:${TAG}" }
        failure { echo 'Pipeline en echec, voir les logs ci-dessus' }
    }
}
