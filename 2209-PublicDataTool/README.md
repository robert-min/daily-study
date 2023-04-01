# Public Data Tool

## Blog
[link](https://github.com/robert-min/dev-blog/issues?q=label%3APubicDataTool+is%3Aclosed)

## Preview
![image](https://user-images.githubusercontent.com/91866763/229281093-87483d43-941e-48ed-bfc3-43fc425c48e2.png)

### Django 기본환경 구축

- 개인프로젝트로 Django 웹 개발 프레임워크를 처음 사용했지만, Flask를 통해 가지고 있던 기본 웹 개발 지식과 Django 공식 문서를 통해 필요한 부분을 공부하면서 진행
- Public Data Tool 프로젝트 안에 category와 tool 두 애플리케이션으로 구성
    - 이번 1차의 경우 데이터 수집 영역 구축에 집중했기 때문에 Category 앱 작업에 집중
    - Tool의 경우 2차 프로젝트 진행 시 작업


Django 프로젝트 진행 시 자주 사용한 명령어 정리
```sh
# 일반적으로 Pycharm Django 템플릿을 활용할 경우 기본 구성이 가능하지만,
# 체계적인 작업 파일 관리를 위해 config를 통해 기본 구성 파일을 만들고 진행
# 프로젝트 생성 : config는 기본 앱 경로명, "." 현재 경로에 생성
django-admin startproject config .

# migrate : 장고의 마이그레이션은 모델의 변경 내용을 DB스키마에 적용하는 방법
# 이번 1차 프로젝트의 경우 장고 ORM을 사용하지 않았기 때문에 model를 따로 작업하지는 않음.
python3 manage.py migrate

# 계정생성
# django는 프로젝트 생성 시 기본적으로 admin을 제공하고 있고 admin접속하기 위한 계정 생성
python3 manage.py createsuperuser

# 앱 생성
python3 manage.py start app {앱 이름}
# 앱 생성 후 config/setting.py -> INSTALLED_APPS에 앱 이릅 추가

# 앱 별로 있는 static 파일 프로젝트 static 경로로 모으기
# config/setting.py에 static 경로 설정
'''python
	STATIC_URL = '/static/'
	
	STATICFILES_DIRS = [
	    os.path.join(BASE_DIR, 'category', 'static')
	]
	
	STATIC_ROOT = os.path.join(BASE_DIR, 'static')
'''
# static 파일 모으기
python3 manage.py collectstatic

# 앱 실행
python3 manage.py runserver
```
### 프론트 작업(Html, Bootstrap)

- PDT 프로젝트를 진행하면서 가장 어려웠던 부분이 프론트 지식이 0이었던 점!!
- 부트스트랩을 사용해 진행했지만 디테일한 부분을 작업하는데 많은 어려움이 존재
- GNB의 경우 모든 페이지 들어가기 때문에 기본 base.html에 작업하고 나머지 페이지에서는 base.html을 상속받아서 사용하는 것으로 구성
- templates/base.html
    - 각 페이지 별로 작업하는 부분은 block을 통해 처리
    - 페이지 로딩 속도 등 작업을 위해 jquery 호출 위치 등 조정 등이 필요하지만, 현재는 이와 관련된 지식이 없기 때문에 구현에 초점을 맞춰서 진행

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
<!--    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">-->

    <title>{% block title%}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css" rel="stylesheet"
          integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.5/dist/umd/popper.min.js"
            integrity="sha384-Xe+8cL9oJa6tN/veChSP7q+mnSPaj5Bcu9mPX5F5xIGE0DVittaqT5lorf0EI7Vk"
            crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.min.js"
            integrity="sha384-ODmDIVzN+pFdexxHEHFBQH3/9/vQ9uori45z4JjnFsRydbmQbmL5t1tQ0culUzyK"
            crossorigin="anonymous"></script>

    {% block script %}
    {% endblock %}

    {% block style %}
    {% endblock %}
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'category:tool_all' %}">DataTool</a>
            <form class="d-flex" role="search" style="float: right">
<!--                <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search">-->
                <button class="btn btn-outline-success" type="submit">Menu</button>
            </form>
        </div>
    </nav>

    <div class="container">
        {% block content %}
        {% endblock %}
    </div>
</body>
</html>
```

- 각 페이지의 html 작업은 아래와 같이 상속을 받아서 진행
    - title은 title block에, body에 들어갈 content는 content block에 작업

```html
{% extends 'base.html' %}

{% block title %}Loading Page

{% endblock %}

{% block content %}
    <a class="btn btn-primary" href="{% url 'category:tool_all' %}" role="button">홈화면으로 이동하기</a>
{% endblock %}
```

### 비동기 처리 - CSV 파일 json 변환

- 앞 내용과 동일하게 프론트 지식이 전혀 없는 상태에서 진행했기 때문에, 프로젝트 진행에서 많은 시행착오가 있었던 부분
- 테스트 환경에서는 데이터가 적은 csv 파일을 사용했기 때문에 처리 시간에 문제가 없었지만, 실제 환경에서는 몇 GB의 데이터를 처리할 수 도 있음.
- 이를 프론트 상에서 처리하기에는 문제가 있기 때문에 서버에 요청하고 처리 실행 결과를 기다릴 필요가 없는 비동기 async로 처리가 필요
- static/upload/csvtojson.javascript

```jsx
function handleFileLoad(event){

    let uploaded = event.target.result;
    // csvJson 함수 호출
    let upload_data = csvJson(uploaded)

    $.ajax({
        // 요청될 URL 주소
        url: 'ajax_method',
        type: "POST",
        dataType: "JSON",
        data: {
            'upload_data': upload_data,
            csrfmiddlewaretoken: "{{ csrf_token }}"
        },
        headers: { "X-CSRFToken": "{{ csrf_token }}"},

        success: function (data) {
            const port_data = JSON.stringify(data);
            var port_data_json = JSON.parse(port_data);
        },

        error : function (xhr, textStatus, thrownError) {
            alert("Error. Can't send URL to Django : " + xhr.status + ":" + xhr.responseText);
        }
    });
}
```

- category/views.py

```python
# ajax로 받아온 json 데이터 처리
@csrf_exempt
def ajax_method(request):
    if request.method == "POST" and index:
        uploaded = request.POST.get('upload_data', None)
        uploaded_list = json.loads(uploaded)
        push_elasticsearch(uploaded_list, index)
        message = "통신 성공"
        context = {"message": message}
        return HttpResponse(json.dumps(context), content_type="application/json")
```

- 성능보다는 구현에 초점을 맞춰서 코드를 작업했기 때문에, 실제 테스트를 진행할 경우 많은 오류가 발생할 것으로 예상!!

### Elasticsearch DB 연결

- Elasticsearch 환경 구축의 경우 EC2 환경에서 구축한 내용은 이전 글에 작성했고 맥 환경의 경우 아래 사이트를 통해 쉽게 구축할 수 있기 때문에 따로 정리X
- [https://www.elastic.co/guide/en/elasticsearch/reference/7.17/brew.html](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/brew.html)
- Elasticsearch 구축 후 Django에서 Index 명과 json 데이터를 받아 저장하는 작업 진행
- Index 명은 Django Form을 통해 사용자가 직접 입력하도록 코드 구현
    - category/form.py
    
    ```python
    from django import forms
    
    class IndexForm(forms.Form):
        index_name = forms.CharField(label="Set index", max_length=10)
    ```
    
    - category/templates/upload.html
    
    ```html
    <form action="{% url 'category:upload' %}" method="post">
        {% csrf_token %}
        {{ form }}
    </form>
    
    ```
    
- 사용자가 입력한 Index 명과 데이터를 Elasticsearch 처리하는 함수 실행
    - category/views.py
    
    ```python
    # 사용자가 설정한 index 명철
    def upload_csv(request):
        global index
        if request.method == "POST":
            form = IndexForm(request.POST)
            if form.is_valid():
                index = form.cleaned_data["index_name"]
        else:
            index = ""
            form = IndexForm()
        return render(request, 'category/upload.html', {'form': form})
    
    # ajax로 받아온 json 데이터 처리
    @csrf_exempt
    def ajax_method(request):
        if request.method == "POST" and index:
            uploaded = request.POST.get('upload_data', None)
            uploaded_list = json.loads(uploaded)
            push_elasticsearch(uploaded_list, index)
            message = "통신 성공"
            context = {"message": message}
            return HttpResponse(json.dumps(context), content_type="application/json")
    ```
    
- category/elasticsearch.py
    - bulk를 통해 Elasticsearch DB에 전달


```python
from collections import deque
import elasticsearch7
from elasticsearch7 import helpers

def readline(all_data):
    # 수정 : jqeury에서 마지막 빈데이터 전송하는 부분 처리 필요!!(현재는 파이썬 코드에서 처리)
    for line in all_data[:-1]:
        yield line


def push_elasticsearch(data, idx):
    es = elasticsearch7.Elasticsearch(["http://localhost:9200"])

    # tourist => web에서 인덱스 명 설정
    es.indices.delete(index=idx, ignore=404)
    deque(helpers.parallel_bulk(es, readline(data), index=idx), maxlen=0)
    es.indices.refresh()
    
 ```
 
 ### 1차 진행사항 이미지

- upload.html

![image](https://user-images.githubusercontent.com/91866763/229281301-6d3eb09a-84d7-4b25-9bb4-89ba07467297.png)

- Elasticsearch 저장 확인

![image](https://user-images.githubusercontent.com/91866763/229281312-3443e91f-f5d4-47ed-8ca7-d9def3f34a9a.png)
