import evennia

from datetime import datetime

from evennia.objects.objects import DefaultObject, DefaultCharacter
from collections.abc import MutableMapping


def __get_player(id: int) -> DefaultCharacter | None:
    results = evennia.search_object(f"#{id}")
    if len(results) > 0:
        return results[0]
    else:
        return None


class JobsComment:
    # regular fields
    text: str = ""
    visibility: int = 0

    # translated fields
    raw_source: int = 0
    raw_sent: float = 0.0

    def __init__(self, text: str = '', vis: int = 0, raw_source: int = 0, raw_sent: float = 0.0):
        self.raw_source = raw_source
        self.text = text
        self.raw_sent = raw_sent
        self.visibility = vis

    @property
    def sources(self) -> DefaultCharacter | None:
        return __get_player(self.raw_source)

    @property
    def sent(self) -> datetime:
        return datetime.fromtimestamp(self.raw_sent)


class JobsJob:
    # regular fields
    id: int = 0
    title: str = ''
    comments: list[JobsComment] = []

    # calculated fields
    raw_owner: int = 0
    raw_opened_on: float = 0.0
    raw_sources: list[int] = []

    def __init__(self, id: int = 0, title: str = '', comments: list[JobsComment] = [], raw_owner: int = 0, raw_opened_on: float = 0.0, raw_sources: list[int] = []):
        self.id = id
        self.title = title
        self.comments = comments
        self.raw_owner = raw_owner
        self.raw_opened_on = raw_opened_on
        self.raw_sources = raw_sources

    @property
    def owner(self) -> DefaultCharacter | None:
        return __get_player(self.raw_owner)

    @owner.setter
    def owner(self, value: DefaultCharacter):
        self.raw_owner = value.id

    @property
    def opened_on(self) -> datetime:
        return datetime.fromtimestamp(self.raw_opened_on)

    @property
    def sources(self) -> tuple[DefaultCharacter, ...]:
        return (__get_player(id) for id in self.raw_sources)

    # We don't want to use a setter because we have disparate types
    def update_sources(self, sources: list[DefaultCharacter]):
        self.raw_sources = [source.id for source in sources]

    def add_comment(self, comment: JobsComment) -> tuple[bool, str]:
        try:
            self.comments.append(comment)
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def delete_comment(self, id: int) -> tuple[bool, str]:
        try:
            if len(self.comments) <= id:
                return (False, "#-1 INVALID COMMENT ID")

            del self.comments[id]
        except Exception as e:
            return (False, str(e))

    def is_source(self, target: DefaultCharacter):
        for player in self.sources:
            if player.id == target.id:
                return True

        return False


class JobsBucket:
    # regular fields
    name: str = ""
    desc: str = ""
    jobs: dict[int, JobsJob] = {}

    # calculated fields

    def __init__(self, name: str, desc: str, jobs: dict[int, JobsJob] = {}):
        self.name = name.upper()
        self.desc = desc
        self.jobs = jobs

    def add_job(self, job: JobsJob) -> tuple[bool, str]:
        try:
            if self.jobs.get(job.id) is not None:
                return (False, "#-1 JOB ID ALREADY EXISTS")

            self.jobs[job.id] = job
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def del_job(self, job_id: int) -> tuple[bool, str]:
        try:
            if self.jobs.get(job_id) is None:
                return (False, "#-1 JOB ID DOES NOT EXIST")

            del self.jobs[job_id]
            return (True, '')
        except Exception as e:
            return (False, str(e))


class JobsDatabase(DefaultObject):
    # regular fields
    buckets: dict[str, JobsBucket] = {}


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
            for bucket in self.data.buckets.values():
                for jobId in bucket.jobs.keys():
                    if jobId > self.__max_id:
                        self.__max_id = jobId

        return self.__max_id

    @property
    def data(self) -> JobsDatabase:
        if self.__instance is None:
            self.__instance = self.__construct_object(self.key)

        return self.__instance

    def has_bucket(self, name: str) -> bool:
        return self.data.buckets.get(name.upper())

    def create_bucket(self, name: str, desc: str) -> tuple[bool, str]:
        if not name.isalpha():
            return (False, "#-1 INVALID BUCKET NAME")

        if self.has_bucket(name):
            return (False, "#-2 BUCKET NAME EXISTS")

        name = name.upper()
        self.data.buckets[name] = JobsBucket(name, desc)
        self.data.save()
        return (True, "")

    def delete_bucket(self, name: str) -> tuple[bool, str]:
        if not self.has_bucket(name):
            return (False, "#-1 INVALID BUCKET")

        name = name.upper()
        del self.data.buckets[name]
        self.data.save()
        return (True, "")

    def find_job_in_all_buckets(self, job_id: int) -> JobsJob | None:
        for bucket in self.data.buckets.values():
            job = bucket.jobs.get(job_id)
            if job is not None:  # We only want to return if we find the job, there may be more buckets to search.
                return job

        return None

    def create_job(self, bucket_name: str = '', source: DefaultCharacter = None, title: str = '', comment: str = '') -> tuple[bool, str]:
        if not self.has_bucket(bucket_name):
            return (False, "#-1 INVALID BUCKET")

        id = self.__MAX_ID + 1

        if source is None:
            return (False, "#-2 INVALID SOURCE")

        try:
            bucket_name = bucket_name.upper()
            self.data.buckets[bucket_name].add_job(JobsJob(
                id=id,
                title=title,
                comments=[JobsComment(
                    text=comment,
                    vis=0,
                    raw_source=source.id,
                    raw_sent=datetime.now().timestamp())],
                raw_owner=0,
                raw_opened_on=datetime.now().timestamp(),
                raw_sources=[source.id]))

        except Exception as e:
            return (False, str(e))
        else:
            self.__max_id = id

        self.data.save()
        return (True, "")

    def delete_job(self, job_id: int) -> tuple[bool, str]:
        try:
            found_bucket = None

            for bucket in self.data.buckets.values():
                if bucket.jobs.get(job_id) is not None:
                    found_bucket = bucket
                    break

            if found_bucket is None:
                return (False, "#-1 INVALID JOB ID")

            found_bucket.del_job(job_id)
            self.data.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def add_comment(self, job_id: int = 0, comment: str = "", source: DefaultCharacter = None, vis: int = 0) -> tuple[bool, str]:
        try:
            if source is None:
                return (False, "#-2 INVALID SOURCE")

            job = self.find_job_in_all_buckets(job_id)
            if job is None:
                return (False, "#-1 INVALID JOB ID")

            job.add_comment(JobsComment(comment, vis, source.id, datetime.now().timestamp()))
            self.data.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def delete_comment(self, job_id: int, comment_id: int) -> tuple[bool, str]:
        try:
            job = self.find_job_in_all_buckets(job_id)
            if job is None:
                return (False, "#-1 INVALID JOB ID")

            comment = job.comments[comment_id - 1]
            if comment is None:
                return (False, "#-2 INVALID COMMENT ID")

            job.delete_comment(comment_id)
            self.data.save()
            return (True, "")
        except Exception as e:
            return (False, str(e))
