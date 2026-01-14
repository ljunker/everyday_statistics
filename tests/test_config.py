import os
from src.config import create_app

def test_config_db_dir_creation(tmp_path):
    # Test line 35 of config.py: os.makedirs(db_dir, exist_ok=True)
    db_dir = tmp_path / "new_db_dir"
    db_file = db_dir / "stats.db"
    
    # We need to make sure create_app sees this sqlite path
    test_config = {
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_file}',
        'TESTING': True
    }
    
    # This should trigger os.makedirs(db_dir)
    create_app(test_config)
    assert os.path.exists(db_dir)

def test_config_scheduler_init(monkeypatch):
    # Test lines 43-44 of config.py
    # scheduler.init_app(app)
    # scheduler.start()
    # It only runs if test_config and not test_config.get('TESTING', True)
    
    # Mock scheduler to avoid starting actual background threads
    class MockScheduler:
        def __init__(self):
            self.initialized = False
            self.started = False
        def init_app(self, app):
            self.initialized = True
        def start(self):
            self.started = True
    
    mock_sched = MockScheduler()
    monkeypatch.setattr("src.config.get_scheduler", lambda: mock_sched)
    
    create_app({'TESTING': False})
    assert mock_sched.initialized is True
    assert mock_sched.started is True
