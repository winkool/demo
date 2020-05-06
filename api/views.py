import json
import re
from time import time

import jsonschema
import redis
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.schemas import URL_SCHEMA
from demo.settings import REG_URL

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


def get_domain(url: str):
    parsed_url = re.search(REG_URL, url)
    return parsed_url.group(1)


@api_view(['POST'])
def visited_links(request, *args, **kwargs):
    key = 'demo:links'
    try:
        item = json.loads(request.body)

        jsonschema.validate(item, URL_SCHEMA,
                            format_checker=jsonschema.FormatChecker(
                                formats=['link']))

        links = item.get('links')
        data = {}
        for link in links:
            data[link] = time()

        redis_instance.zadd(key, data)
        response = {
            "status": "ok"
        }
    except jsonschema.exceptions.ValidationError as ex:
        response = {"status": {"error": f"{ex.instance} is not valid"}}
        return Response(response, 400)
    except json.decoder.JSONDecodeError:
        response = {"status": {"error": "can't decode json"}}
        return Response(response, 400)
    except Exception as ex:
        response = {"status": {"error": f"Unresolved Exception {ex}"}}
        return Response(response, 500)
    return Response(response, 201)


@api_view(['GET'])
def visited_domains(request, *args, **kwargs):
    key = 'demo:links'
    try:
        min_time = int(request.query_params.get('from', 0))
        max_time = int(request.query_params.get('to', 0))
        if min_time > max_time > 0 or max_time < 0 or min_time < 0:
            raise ValueError

        if max_time == 0:
            max_time = 'inf'
        urls = redis_instance.zrangebyscore(key, min_time, max_time)
        result = set()
        for url in urls:
            domain = get_domain(url.decode("utf-8"))
            result.add(domain)

        response = {"domains": list(result),
                    "status": "OK"
                    }

    except ValueError:
        response = {"status": 'request params is not valid'
                    }
        return Response(response, 400)
    except Exception as ex:
        response = {"status": {"error": f"Unresolved Exception {ex}"}}
        return Response(response, 500)
    return Response(response, 200)
