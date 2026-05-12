pipeline {
    agent any

    environment {
        GITLAB_REPO  = "https://gitlab.com/YosraBoubaker/tp-gitlab.git"
        DOCKER_IMAGE = "yosrabenboubaker/flask-products-api"
        DOCKER_TAG   = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('📥 Clonage GitLab') {
            steps {
                echo 'Clonage du dépôt GitLab...'
                git branch: 'develop',
                    url: "${env.GITLAB_REPO}",
                    credentialsId: 'gitlab-credentials'
            }
        }

        stage('📦 Installation dépendances') {
            steps {
                echo 'Installation des dépendances Python...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('🧪 Exécution des tests') {
            steps {
                echo 'Lancement des tests unitaires...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v
                '''
            }
        }

        stage('🐳 Docker Build') {
            steps {
                echo "Construction de l'image Docker..."
                sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('🚀 Docker Push') {
            steps {
                echo 'Publication sur Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline exécuté avec succès !'
        }
        failure {
            echo '❌ Pipeline échoué !'
        }
        always {
            echo '🔚 Fin du pipeline.'
            sh 'docker system prune -f || true'
            cleanWs()
        }
    }
}
