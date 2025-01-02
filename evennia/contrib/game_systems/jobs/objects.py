import evennia

from datetime import datetime

from evennia.objects.objects import DefaultObject, DefaultCharacter
from collections.abc import MutableMapping


def __get_player(id: str) -> DefaultCharacter | None:
    results = evennia.search_object(id)
    if len(results) > 0:
        return results[0]
    else:
        return None


class JobsComment:
    __dict: dict = None

    __id = 0

    def __init__(self, id: int, data: dict):
        self.__id = id
        self.__dict = data

    def __init__(self, id: int, source: str, text: str, sent: datetime, vis: int):
        self.__id = id
        self.__dict = {
            'source': source,
            'text': text,
            'sent': sent.timestamp(),
            'vis': vis
        }

    @property
    def id(self) -> int:
        return self.__id

    @property
    def sources(self) -> DefaultCharacter | None:
        return __get_player(self.__dict.get('sources') or '')

    @property
    def text(self) -> str:
        return self.__dict.get('text') or ""

    @property
    def sent(self) -> datetime:
        return datetime.fromtimestamp(self.__dict.get('sent'))

    @property
    def visibility(self) -> int:
        return self.__dict.get('vis')

    @visibility.setter
    def visibility(self, vis: int):
        self.__dict['vis'] = vis

    def to_dict(self) -> dict:
        return {self.id: self.__dict}


class JobsCommentList(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key: int) -> JobsComment:
        return JobsComment(key, self.store[self._keytransform(key)])

    def get(self, key: int) -> JobsComment | None:
        try:
            return self.__getitem__(key)
        except KeyError as ke:
            return None

    def __setitem__(self, key: int, value: JobsComment):
        self.store[self._keytransform(key)] = value.to_dict()

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)

    def items(self) -> list[tuple[int, JobsComment]]:
        return [(key, self.__getitem__(key)) for key in iter(self.store)]

    def values(self) -> list[JobsComment]:
        return [self.__getitem__(key) for key in iter(self.store)]

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        return key

    def to_raw_dict(self) -> dict[int, dict]:
        return self.store

    @property
    def max_id(self) -> int:
        return max(self.keys())


class JobsJob:
    __dict: dict = None

    id: int = 0

    def __init__(self, id: int, data: dict):
        self.id = id
        self.__dict = data

    @staticmethod
    def construct(id: int, title: str, source_id: str, first_comment: JobsComment) -> 'JobsJob':
        obj = JobsJob(id, {
            'title': title,
            'sources': [source_id],
            'comments': first_comment.to_dict()
        })

        return obj

    @property
    def owner(self) -> DefaultCharacter | None:
        return __get_player(self.__dict.get('owner') or '')

    @owner.setter
    def owner(self, value: DefaultCharacter):
        self.__dict['owner'] = value.id

    @property
    def opened_on(self) -> datetime:
        return datetime.fromtimestamp(self.__dict.get('opened_on'))

    @property
    def sources(self) -> tuple[DefaultCharacter, ...]:
        if self.__dict.get('sources') is None:
            self.__dict['sources'] = []
        return (__get_player(id) for id in self.__dict['sources'])

    # We don't want to use a setter because we have disparate types
    def update_sources(self, sources: list[DefaultCharacter]):
        self.__dict['sources'] = [source.id for source in sources]

    @property
    def title(self) -> str:
        return self.__dict.get('title') or ""

    @title.setter
    def title(self, value: str):
        self.__dict['title'] = value

    @property
    def comments(self) -> JobsCommentList:
        if self.__dict('comments') is None:
            self.__dict['comments'] = {}
        return JobsCommentList(self.__dict['comments'])

    def add_comment(self, comment: JobsComment) -> tuple[bool, str]:
        try:
            self.comments[(self.comments.max_id + 1)] = comment
            return (True, "")
        except Exception as e:
            return (False, str(e))
        
    def delete_comment(self, id: int) -> tuple[bool, str]:
        try:
            if self.comments.get(id) is None:
                return (False, "#-1 INVALID COMMENT ID")
            
            del self.comments[id]
        except Exception as e:
            return (False, str(e))

    def is_source(self, target: DefaultCharacter):
        for player in self.sources:
            if player.id == target.id:
                return True

        return False


class JobsJobList(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key: int) -> JobsJob:
        return JobsJob(key, self.store[self._keytransform(key)])

    def get(self, key: int) -> JobsJob | None:
        try:
            return self.__getitem__(key)
        except KeyError as ke:
            return None

    def __setitem__(self, key: int, value: JobsJob):
        self.store[self._keytransform(key)] = value.to_dict()

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)

    def items(self) -> list[tuple[int, JobsJob]]:
        return [(key, self.__getitem__(key)) for key in iter(self.store)]

    def values(self) -> list[JobsJob]:
        return [self.__getitem__(key) for key in iter(self.store)]

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        return key

    def to_raw_dict(self) -> dict[int, dict]:
        return self.store


class JobsBucket:
    __dict: dict = None

    name: str = ""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.__dict = data

    @property
    def desc(self) -> str:
        return self.__dict.get('desc') or ""

    @desc.setter
    def desc(self, value: str):
        self.__dict['desc'] = value

    @property
    def jobs(self) -> JobsJobList:
        if self.__dict.get('jobs') is None:
            self.__dict['jobs'] = {}
        return JobsJobList(self.__dict.get('jobs'))

    def add_job(self, id: int, job: JobsJob) -> tuple[bool, str]:
        try:
            self.jobs[id] = job
            return (True, "")
        except Exception as e:
            return (False, str(e))
    
    def delete_job(self, id: int) -> tuple[bool, str]:
        try:
            if self.jobs.get(id) is None:
                return (False, "#-1 INVALID JOB ID")
            
            del self.jobs[id]
        except Exception as e:
            return (False, str(e))


class JobsDatabase(DefaultObject):

    @property
    def buckets(self) -> dict[str, JobsBucket]:
        if self.db.buckets is None:
            self.db.buckets = {}
        return {name: JobsBucket(name, data) for name, data in self.db.buckets.items()}


class JobsDatabaseManager:
    key: str = "Jobs::JobsDatabase"
    __max_id: int = 0
    __instance: JobsDatabase = None

    def __construct_object(self, key) -> JobsDatabase:
        found_objs = evennia.search_object(key)
        if found_objs and len(found_objs) == 1:
            return found_objs[0]
        elif len(found_objs) > 1:
            raise Exception("Found multiple objects for key: " + key)

        # else we have none, so carry on.

        obj = evennia.create_object(JobsDatabase, key=key, location="#1")
        return obj

    @property
    def __MAX_ID(self) -> int:
        if self.__max_id == 0:
            for bucket in self.instance.buckets.values():
                for jobId in bucket.jobs.keys():
                    if jobId > self.__max_id:
                        self.__max_id = jobId

        return self.__max_id

    @property
    def instance(self) -> JobsDatabase:
        if self.__instance is None:
            self.__instance = self.__construct_object(self.key)

        return self.__instance

    def has_bucket(self, name: str) -> bool:
        for bucket in self.instance.buckets.keys():
            if bucket.upper() == name.upper():
                return True

        return False

    def create_bucket(self, name: str, desc: str) -> tuple[bool, str]:
        if not name.isalpha():
            return (False, "#-1 INVALID BUCKET NAME")

        if self.has_bucket(name):
            return (False, "#-2 BUCKET NAME EXISTS")

        name = name.upper()
        self.instance.buckets[name] = JobsBucket(name, {'desc': desc, 'jobs': {}})
        self.instance.save()
        return (True, "")

    def delete_bucket(self, name: str) -> tuple[bool, str]:
        if not self.has_bucket(name):
            return (False, "#-1 INVALID BUCKET")

        name = name.upper()
        self.instance.buckets = self.instance.buckets.pop(name)
        self.instance.save()
        return (True, "")

    def find_job(self, job_id: int) -> JobsJob | None:
        for bucket in self.instance.buckets.values():
            job = bucket.jobs.get(job_id)
            if job is not None:  # We only want to return if we find the job, there may be more buckets to search.
                return job

        return None

    def create_job(self, bucket_name: str, source_id: str, title: str, comment: str) -> tuple[bool, str]:
        if not self.has_bucket(bucket_name):
            return (False, "#-1 INVALID BUCKET")

        id = self.__MAX_ID + 1
        source = __get_player(source_id)

        if source is None:
            return (False, "#-2 INVALID SOURCE")

        try:
            bucket_name = bucket_name.upper()
            self.instance.buckets[bucket_name].jobs[id] = JobsJob.construct(
                id, title, source_id, JobsComment(1, source, comment, datetime.now(), 1))

        except Exception as e:
            return (False, str(e))
        else:
            self.__max_id = id

        self.instance.save()
        return (True, "")

    def delete_job(self, job_id: int) -> tuple[bool, str]:
        found_bucket = None

        for bucket in self.instance.buckets.values():
            if bucket.jobs.get(job_id) is not None:
                found_bucket = bucket
                break

        if found_bucket is None:
            return (False, "#-1 INVALID JOB ID")

        found_bucket.jobs = found_bucket.jobs.pop(job_id)
        self.instance.buckets[bucket.name] = found_bucket

        self.instance.save()
        return (True, "")

    def add_comment(self, job_id: int, comment: str, source_id: str, vis: int) -> tuple[bool, str]:
        try:
            job = self.find_job(job_id)
            if job is None:
                return (False, "#-1 INVALID JOB ID")

            comm_id = max(job.comments.keys() or [0]) + 1

            comment = JobsComment(comm_id, source_id, comment, datetime.now(), vis)
            job.comments[comm_id] = comment

            self.instance.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def delete_comment(self, job_id: int, comment_id: int) -> tuple[bool, str]:
        try:
            job = self.find_job(job_id)
            if job is None:
                return (False, "#-1 INVALID JOB ID")

            comment = job.comments.get(comment_id)
            if comment is None:
                return (False, "#-2 INVALID COMMENT ID")

            job.comments = job.comments.pop(comment_id)
            self.instance.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def update_source(self, job_id: int, source_ids: list[str]) -> tuple[bool, str]:
        try:
            job = self.find_job(job_id)
            if job is None:
                return (False, "#-1 INVALID JOB ID")

            job.source = "|".join(source_ids)
            self.instance.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))
