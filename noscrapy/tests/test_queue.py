from noscrapy import Job, Queue


def test_add_jobs():
    q = Queue()
    job = Job('http://test.lv/', {})
    q.add(job)
    assert 1 == q.get_queue_size()
    assert 'http://test.lv/' == q.jobs[0].url

def test_mark_urls_scraped():
    q = Queue()
    job = Job('http://test.lv/', {})
    q.add(job)
    q.get_next_job()
    assert 0 == q.get_queue_size()

    # try add this job again
    q.add(job)
    assert 0 == q.get_queue_size()

def test_reject_documents():
    q = Queue()
    job = Job('http://test.lv/test.doc')
    assert not q.add(job)
    assert 0 == q.get_queue_size()
