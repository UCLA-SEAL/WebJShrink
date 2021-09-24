#!/usr/bin/python3.6
import subprocess
import re
from subprocess import call
from threading import Lock
import json
import sys
import os
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file
import csv
import os.path
import time
from pathlib import Path

javaPath = 'java'
githubUrl = 'https://github.com/'
jarName = 'webjshrink.jar'

app = Flask(__name__)
app.secret_key = 'ed603f6ba92e4c112a70b8b1e97451871d86e592039b77ad'

ALLOWED_ORIGINS = ['https://mihirmathur.github.io', 'http://localhost:3000']

mutex = Lock()


@app.route("/")
def hello():
    """
    Route to check if server is running
    """
    return "Hello World!"


@app.route("/analysis/<user>/<repo>", methods=['GET'])
def analysis(user, repo):
    """
    Route to download GitHub repo and run complete API analysis.
    take in options for call graph analysis and run javaPrep script
    """
    gURL = 'https://github.com/' + user + '/' + repo + '.git'

    WEB_JSHRINK_CALL = javaPath + " -jar " \
        "../java-dependencies/{} ".format(jarName) + \
        "--maven-project tmp/{} ".format(repo) + \
        "--webjshrink {} --verbose --log-directory tmp/data/{} ".format(repo, repo) + \
        "--skip-method-removal "

    spark = int(request.args.get('spark'))
    tamiflex = int(request.args.get('tamiflex'))
    jmtrace = int(request.args.get('jmtrace'))

    if spark:
        WEB_JSHRINK_CALL += "--use-spark "
    if tamiflex:
        WEB_JSHRINK_CALL += "--tamiflex ../java-dependencies/poa-2.0.3.jar "
    if jmtrace:
        WEB_JSHRINK_CALL += "--jmtrace ../java-dependencies/ "

    entryPoints = ""  # for cache file name
    if int(request.args.get('mainEntry')):
        WEB_JSHRINK_CALL += "--main-entry "
        entryPoints += "-main"
    if int(request.args.get('publicEntry')):
        WEB_JSHRINK_CALL += "--public-entry "
        entryPoints += "-public"
    if int(request.args.get('testEntry')):
        WEB_JSHRINK_CALL += "--test-entry "
        entryPoints += "-test"
    print(WEB_JSHRINK_CALL)

    # merged string <repo_name>-[entry point options]-[spark|CHA]
    cachedFileName = repo + entryPoints + \
        ('-spark' if spark else '-CHA') + \
        ("-tam" if tamiflex else '') + \
        ("-jmt" if jmtrace else '')

    # run CGA if there is no cached file
    if not (os.path.isfile("tmp/" + cachedFileName + ".json")):
        # prep environment and fire off CGA
        javaPrep(gURL, repo)
        call(WEB_JSHRINK_CALL, shell=True)
    else:
        print(repo + " already exists in cache. Skipping download and install...")
        time.sleep(7)  # remove after demo

    # read in data
    try:
        with open('tmp/' + cachedFileName + '.json') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        response = jsonify(
            error="Error building Maven Project, Please Try another Maven Project")
        if request.headers['Origin'] in ALLOWED_ORIGINS:
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add(
                'Access-Control-Allow-Origin', request.headers['Origin'])
        return response

    response = jsonify(data)
    response.set_cookie('cachedFileName', cachedFileName)
    response.set_cookie('cachedGitHubURL', gURL)
    if request.headers['Origin'] in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin',
                             request.headers['Origin'])
    print(response)
    return response


def javaPrep(gURL, repo):
    """
    prepares maven environment
    """
    if gURL:
        if not (os.path.isdir('tmp')):
            call('mkdir tmp', shell=True)
        os.chdir('tmp')

        # clone and make necessary folders
        call('rm -rf {}'.format(repo), shell=True)
        call('git clone {}'.format(gURL), shell=True)
        if not (os.path.isdir('../tmp_debloat')):
            call('mkdir ../tmp_debloat', shell=True)
        if not (os.path.isdir('resources')):
            call('mkdir resources', shell=True)
        if not (os.path.isdir('data/{}'.format(repo))):
            call('mkdir data/{}'.format(repo), shell=True)
        if not (os.path.isdir('chk')):
            call('mkdir chk', shell=True)

        gitDir = str(subprocess.check_output(
            ['pwd']), sys.stdout.encoding).strip() + '/' + repo
        print('Cloned repo and created necessary folders...')
    else:
        os.chdir('tmp_debloat')
        gitDir = repo

    try:
        os.chdir(gitDir)
    except Exception as e:
        raise e

    # now we want to set up the environment
    with mutex:
        # get rid of libs you might have altered before
        p = subprocess.Popen('mvn clean && rm -rf ' + gitDir +
                             '/libs', stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        print('Finished mvn clean...')

        p = subprocess.Popen('mvn install -Dmaven.repo.local=' + gitDir +
                             '/libs -DskipTests', stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        print('Finished mvn install...')

        p = subprocess.Popen('mvn dependency:build-classpath -Dmaven.repo.local=' +
                             gitDir + '/libs &> onr_classpath_new.log', stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        print('Finished building class path...')

        os.chdir('../..')


def runMvnTests(folderName):
    """
    Runs $ mvn test

    Captures output for failed tests / total number tests

    Note:
      Makes assumption debloat() has been called on repo
    """
    if not os.path.isdir('tmp_debloat/{}'.format(folderName)):
        print('Incorrect folder name!')
        return 0, 0

    os.chdir('tmp_debloat/{}'.format(folderName))
    mvnTestOutput = str(
        subprocess.check_output(['mvn', 'test']),
        sys.stdout.encoding).strip()

    if not mvnTestOutput:
        print('Error performing mvn test command!')
        os.chdir('../..')
        return 0, 0

    # capture relevant lines of output
    resIdx = mvnTestOutput.find('Results :')
    if resIdx == -1:
        print('Error finding \"Results :\" keyword in mvn output')

    lines = [l.strip() for l in mvnTestOutput[resIdx:].split('\n') if l]
    if len(lines) < 2:
        print('Error parsing mvn test output!')
        os.chdir('../..')
        return 0, 0

    # Line after results: 'Tests run: X, Failures: Y'
    results = lines[1]
    numTests = numTestsFailed = 0
    for entry in results.split(','):
        info, data = entry.split(': ')
        if info == "Tests run":
            numTests = int(data)
        elif info == "Failures":
            numTestsFailed = int(data)

    # return
    os.chdir('../..')
    return numTests, numTestsFailed


# Route to trigger jdebloat on repo.
@app.route("/debloat/<repo>", methods=['GET'])
def debloat(repo):
    """
    Triggers debloating process. Creates a copy of the repo
    to debloat, and then returns the after data
    """
    print('Received Debloat Request...')
    print(request)

    # adjust previouslu cached file name
    lastCache = request.cookies.get('cachedFileName')
    cachedDebloatName = lastCache

    # add further detail to debloated file name
    prune, removeMethods, checkpointing = '', '', ''
    if int(request.args.get('pruneApp')):
        prune = "--prune-app "
        cachedDebloatName += "-prune"
    if int(request.args.get('removeMethods')):  # remove header and body, default is just header
        removeMethods = "--remove-methods "
        cachedDebloatName += "-all"
    if int(request.args.get('removeMethodBodyWithMessage')):
        message = request.args.get('removeBodyMessage')
        removeMethods = "--include-exception " + message + " "
        cachedDebloatName += "-msg"
    if int((request.args.get('checkpointing'))):
        checkpointing = "--checkpoint tmp/chk/"
        cachedDebloatName += "-chk"

    # check for existing zip for quick debloat return
    if (os.path.isfile('tmp_debloat/dblt-{}.json'.format(cachedDebloatName)) and
            os.path.isfile('tmp_debloat/{}.zip'.format(cachedDebloatName))):

        print("Debloated " + cachedDebloatName +
              " already exists in cache. Skipping debloat process.")
        time.sleep(7)  # remove after demo

        with open('tmp_debloat/dblt-{}.json'.format(cachedDebloatName)) as f:
            debloatInfo = json.load(f)
            response = jsonify(debloatInfo)
            response.set_cookie('cachedDebloatName', cachedDebloatName)
            if request.headers['Origin'] in ALLOWED_ORIGINS:
                response.headers.add(
                    'Access-Control-Allow-Credentials', 'true')
                response.headers.add(
                    'Access-Control-Allow-Origin', request.headers['Origin'])
            print(response)
            return response

    # Otherwise, go through entire debloat process....
    call('rm -fr tmp_debloat/{}'.format(cachedDebloatName), shell=True)
    os.chdir('tmp_debloat')
    call('git clone {}'.format(request.cookies.get('cachedGitHubURL')), shell=True)
    os.chdir('..')
    call('mv tmp_debloat/{} tmp_debloat/{}'.format(repo,
                                                   cachedDebloatName), shell=True)  # rename

    # create tmp folders for deblaoting
    if not (os.path.isdir('tmp_debloat/data/{}'.format(cachedDebloatName))):
        call('mkdir tmp_debloat/data/{}'.format(cachedDebloatName), shell=True)
    if not (os.path.isdir('../tmp/chk/{}'.format(cachedDebloatName))):
        call('mkdir ../tmp/chk/{}'.format(cachedDebloatName), shell=True)

    # update checkpointing
    if checkpointing:
        checkpointing += cachedDebloatName + " "

    # build debloat call string
    DEBLOAT_CALL = javaPath + " -jar " \
        "../java-dependencies/{} --maven-project ".format(jarName) + \
        "tmp_debloat/{} --log-directory tmp_debloat/data/{} ".format(cachedDebloatName, cachedDebloatName) \
        + prune + removeMethods + checkpointing

    if ("spark" in cachedDebloatName):
        DEBLOAT_CALL += "--use-spark "
    if ("tam" in cachedDebloatName):
        DEBLOAT_CALL += "--tamiflex ../java-dependencies/poa-2.0.3.jar "
    if ("jmt" in cachedDebloatName):
        DEBLOAT_CALL += "--jmtrace ../java-dependencies "

    # add entry points
    for entry in lastCache.split('-')[1:-1]:
        if entry in ['main', 'public', 'test']:
            DEBLOAT_CALL += "--" + entry + "-entry "
    DEBLOAT_CALL += "--verbose"
    print(DEBLOAT_CALL)

    # fire off debloating process
    debloatInfo = {}
    try:
        print('Firing off debloat process...')
        javaPrep("", cachedDebloatName)
        call(DEBLOAT_CALL, shell=True)

        # creates json of debloat data
        with open('tmp_debloat/data/{}/log.dat'.format(cachedDebloatName)) as f:
            debloatData = f.readlines()

        for line in debloatData:
            lineData = line.split(',')
            key, val = lineData[0], lineData[1].strip()

            debloatInfo[key] = val
            if 'after' in key:  # percent reductions
                shortKey = "_".join(key.split('_')[:-1])
                denominator = float(debloatInfo[shortKey + "_before"])
                if denominator != 0:
                    debloatInfo[shortKey + "_reduction"] = round(
                        (denominator - int(debloatInfo[key]))/denominator, 3)*100.0
                    # for the .000001 bug
                    debloatInfo[shortKey + "_reduction"] = round(
                        debloatInfo[shortKey + "_reduction"], 1)
                else:
                    debloatInfo[shortKey + "_reduction"] = 0

        print('Firing off mvn test...')
        totalNumberTests, totalTestsFailed = runMvnTests(cachedDebloatName)
        debloatInfo['total_number_tests'] = totalNumberTests
        debloatInfo['total_tests_failed'] = totalTestsFailed
        print('Finished mvn test...')

        # write to json
        with open('tmp_debloat/dblt-' + cachedDebloatName + '.json', 'w+') as f:
            json.dump(debloatInfo, f)

        # create zip of repo
        # change to cache_file_name
        repoLocation = 'tmp_debloat/{}'.format(cachedDebloatName)
        zip_call = 'zip -r ' + repoLocation + '.zip ' + repoLocation + '/'
        call(zip_call, shell=True, stdout=open(os.devnull, 'wb'))

    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        print(str(e))

    # send response back
    response = jsonify(debloatInfo)
    response.set_cookie('cachedDebloatName', cachedDebloatName)
    if request.headers['Origin'] in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin',
                             request.headers['Origin'])
    print(response)
    return response


@app.route('/download/<repo>')
def downloadFile(repo):
    cachedDebloatName = request.cookies.get('cachedDebloatName')
    # change to changed_file name
    repoPath = 'tmp_debloat/{}.zip'.format(cachedDebloatName)
    return send_file(repoPath, as_attachment=True)


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
