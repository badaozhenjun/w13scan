# *_*coding:utf-8 *_*
# *_*coding:utf-8 *_*

import json,time
import jsonpickle
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, create_engine,func,distinct
from sqlalchemy.orm import sessionmaker,scoped_session

# engine = create_engine('sqlite:////root/tools/w13scan/W13SCAN/yuxiao/w13scan_models.db')
engine = create_engine('sqlite:////root/tools/security-scripts/lib/models.db')
Base = declarative_base()

DBSession = scoped_session(sessionmaker(bind=engine,autocommit=True))
class DB:
    @property
    def session(self):
        return DBSession()

db = DB()

class BaseModel(Base):
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self):
        return json.dumps(self.as_dict())

    @staticmethod
    def as_dicts(tasks):
        if not tasks:
            return []
        else:
            result = []
            for task in tasks:
                result.append(task.as_dict())
            return result

    @staticmethod
    def as_jsons(tasks):
        return json.dumps(BaseModel.as_dicts(tasks))
    # def save(self):

    @classmethod
    def get_first_by(cls,**kwargs):
        return db.session.query(cls).filter_by(**kwargs).first()
    @classmethod
    def get_list_by(cls,page_index=None,page_size=None,**kwargs):
        q=db.session.query(cls).filter_by(**kwargs)
        if page_size and page_index:
            page_size = int(page_size)
            page_index = int(page_index)
            total=db.session.query(func.count(cls.id)).scalar()
            records=q.limit(page_size).offset((page_index-1)*page_size)
            return records,total
        return q.all()
    @classmethod
    def get_distinct_by(cls,field=None,page_index=None,page_size=None,**kwargs):
        q=db.session.query(distinct(field)).filter_by(**kwargs)
        if page_size and page_index:
            page_size = int(page_size)
            page_index = int(page_index)
            total=db.session.query(func.count(distinct(field))).scalar()
            records=q.limit(page_size).offset((page_index-1)*page_size)
            return records,total
        return q.all()

    @classmethod
    def delete_by_ids(cls,ids):
        deleted_objects = cls.__table__.delete().where(cls.id.in_(ids))
        db.session.execute(deleted_objects)
        # if len(deleted_objects)==1:
        #     return deleted_objects[0]
        # else:
        #     return deleted_objects

    @classmethod
    def delete_by_id(cls, id):
        return cls.delete_by_ids([id])

    def save_or_update(self):
        if hasattr(self,"create_at") and not self.create_at:
            self.create_at = str(time.time())
        db.session.merge(self)
        db.session.flush()

    @staticmethod
    def get_current_time_str():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __getstate__(self):
        state = {}
        for k, v in self.__dict__.items():
            if k != '_sa_instance_state':
                state[k] = v
        return state

    def __setstate__(self, d):
        self.__dict__ = d
class BugModel(BaseModel):

    __tablename__ = 'bugs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    json = Column(Text(65536))
    url = Column(String(64))
    plugin = Column(String(64))
    create_at = Column(String(64))
    host_domain = Column(String(64))
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.domain)

Base.metadata.create_all(engine)

# model = BugModel(json="{\"aaa\":\"bbbb\",\"cccc\":\"ddddd\"}",url="test1",plugin="plugin2")
# # # import time
# # # # time.sleep(3000)
# model.save_or_update()
# time.sleep(3000)
# for bug in BugModel.get_list_by():
#     BugModel.delete_by_id(bug.id)

# model = DomainModel(domain="www.baidu.com",record_type="CNAME",cname_domain="hahha.com",ip="aaaa",create_at="aaaa",host_domain="baidu.com")
# model.save_or_update()