pipeline {
  agent { label 'docker' }
  stages {
    stage('build') {
      steps {
        script {
          // this pulls an image (groovy:2.4) from docker hub and spins up a container based on it. it exits at the end of the block
          docker.image('anchit2698/testcontainer')
        }

        // if you want the container to stay up until you shut it down,
        // you can use docker run and include the -d (daemon) flag.
        // here i'm also giving the container the name "nginx-oh-yeah":
        sh 'docker run -d anchit2698/testcontainer
      }
    }
  }
}
