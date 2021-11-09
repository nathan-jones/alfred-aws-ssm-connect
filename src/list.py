#!/usr/bin/env python3

import dataclasses
import datetime
import json
import subprocess
import sys
from os import getenv
from pathlib import Path


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class AlfredInstance:
    uid: str
    title: str
    subtitle: str
    arg: str
    type: str

    @classmethod
    def from_dict(cls, d):
        return cls(d['uid'], d['title'], d['subtitle'], d['arg'], d['type'])


def load_from_file(profile):
    cache_dir = getenv('alfred_workflow_cache', getenv('TMPDIR'))
    timeout = int(getenv('cache_timeout_hours', 12))
    profile_cache = Path(cache_dir, profile)
    if not profile_cache.is_file():
        return None
    mtime = datetime.datetime.fromtimestamp(profile_cache.stat().st_mtime)
    now = datetime.datetime.now()
    if now < mtime + datetime.timedelta(hours=timeout):
        text = profile_cache.read_text()
        json_load = json.loads(text)
        instances = []
        for inst in json_load["items"]:
            ainst = AlfredInstance.from_dict(inst)
            instances.append(ainst)
        return instances
    return None


def save_to_file(profile, contents):
    cache_dir = Path(getenv('alfred_workflow_cache', getenv('TMPDIR')))

    if not cache_dir.is_dir():
        cache_dir.mkdir(exist_ok=True)

    profile_cache = Path(cache_dir, profile)
    if profile_cache.exists():
        profile_cache.unlink(missing_ok=True)
    profile_cache.write_text(contents)


def load_from_api(profile):
    aws_bin = getenv('aws_location', '/usr/local/bin/aws')

    instances = subprocess.run([
        aws_bin,
        "ec2",
        "describe-instances",
        "--profile",
        profile,
        "--query",
        "Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0],State.Name]"],
        stdout=subprocess.PIPE).stdout.decode('utf-8')
    json_instances = json.loads(instances)

    instance_list = []
    for instance in json_instances:
        inst = AlfredInstance(
            uid=instance[0][0],
            title=instance[0][1] if instance[0][1] else instance[0][0],
            subtitle=f"{instance[0][0]} - {instance[0][2]}",
            arg=f"{instance[0][0]} --profile {profile}",
            type="file"
        )
        instance_list.append(inst)
    save_to_file(profile, json.dumps({"items": instance_list}, cls=EnhancedJSONEncoder))
    return instance_list


def fetch_instances(profile, host):
    contents = load_from_file(profile)
    if not contents:
        contents = load_from_api(profile)
    instance_list = []

    for instance in contents:
        if host and host.strip():
            keywords = host.split(" ")
            if not all(x in instance.title for x in keywords):
                continue
        instance_list.append(instance)
    return instance_list


def main():
    query = sys.argv[1]
    if ' ' in query:
        (profile, host) = query.split(' ', maxsplit=1)
        if not host:
            host = None
    else:
        (profile, host) = (query, None)

    instances = fetch_instances(profile, host)
    return json.dumps({"items": instances}, cls=EnhancedJSONEncoder)


if __name__ == '__main__':
    print(main())
