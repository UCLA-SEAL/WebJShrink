import subprocess
from subprocess import call
import os
import sys

def main():
    if (len(sys.argv) < 2):
        sys.exit(1)

    repoName = str(sys.argv[1])
    
    # cwd: python_scripts
    os.chdir('tmp/{}'.format(repoName))
    call('mvn dependency:build-classpath -Dmdep.pathSeparator=":" -Dmdep.fileSeparator=":" -Dmdep.outputFile=classpath', shell=True)
    with open('classpath') as f:
        jars = f.read()
    
    # if there is an error reading the classpath info
    if not jars:
        call('mvn dependency:build-classpath -Dmdep.pathSeparator=":" -Dmdep.fileSeparator=":" > classpath', shell=True)
        with open('classpath') as f:
            jarData = f.readlines()
        
        jars = set()
        for line in jarData:
            if '.m2' in line:
                jars.add(line.strip())
        jars = "::".join(list(jars))
    
    # need to match up the jars which say compile
    compileJars = set()
    call('mvn dependency:list > deps.txt', shell=True)
    with open('deps.txt') as f:
        depsOutput = f.readlines()

    for line in depsOutput:
        if ':compile' in line:
            jar = line.strip().split(':')
            jarStr = jar[1] + '-' + jar[3] + '.jar'
            compileJars.add(jarStr)
    compileJars = list(compileJars)

    # clean up final jars
    finalJars = set()
    jars = list(map(lambda x: x.replace(":","/"), jars.split("::")))
    for jar in jars:
        if jar.split('/')[-1] in compileJars:
            finalJars.add(jar)

    # prepend / if missing
    finalJars = list(set(['/' + jar if jar[0] != '/' else jar for jar in list(finalJars)]))
    print(finalJars)
    classesWithJars = []
    for jar in finalJars:
        jarName = jar.split("/")[-1]
        output = subprocess.check_output(['jar','tf',jar]).decode().split('\n')
        for cl in output:
            if ".class" in cl:
                classesWithJars.append(jarName + ":" + cl.replace("/",".")[:-6])
    classesWithJarsData = ','.join(classesWithJars)

    # return to python_scripts/
    os.chdir('../..')
    with open(os.getcwd() + '/tmp/resources/jarData-' + repoName + '.txt','w+') as f:
        f.write(classesWithJarsData)
        
if __name__ == "__main__":
    main()
