from locust import HttpLocust, TaskSet

MAVEN_PROJECTS = [
    "junit-team/junit4"
]

MAVEN_DEBLOAT = []

def cga(l):
    #project = MAVEN_PROJECTS.pop()
    #MAVEN_DEBLOAT.append(project.split('/')[1])
    params = {'mainEntry': '1', 'publicEntry': '0', 'testEntry' : '1', 'spark' : '0', 'cha' : '1', 'tamiflex' : '0'}
    response = l.client.get('/analysis/junit-team/junit4', params=params)
    print(response.text)

def debloat(l):
    #projectName = MAVEN_DEBLOAT.pop()
    params = {'pruneApp' : '1', 'removeMethod' : '1', 'removeOnlyMethodBody' : '0'}
    l.client.get('/debloat/junit4', params=params)

class UserBehavior(TaskSet):
    tasks = {cga: 1, debloat: 1}
    
    def on_start(self):
        cga(self)
    
    def on_stop(self):
        debloat(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000

# locust -f test/locustfile.py --host=https://mihirmathur.github.io/api-analyze/#