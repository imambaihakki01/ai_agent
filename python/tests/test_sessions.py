from nexus_agent.sessions import SessionStore

def test_session_history_and_workspace_isolation(tmp_path):
    store=SessionStore(tmp_path/"sessions.db")
    sid=store.ensure(None,str(tmp_path))
    store.append(sid,"user","hello")
    store.append(sid,"assistant","world")
    assert store.history(sid)==[{"role":"user","content":"hello"},{"role":"assistant","content":"world"}]
    assert store.list(str(tmp_path))[0]["messages"]==2
    try:
        store.ensure(sid,str(tmp_path/"other"))
        assert False, "cross-workspace session should fail"
    except KeyError:
        pass

def test_checkpoint_roundtrip(tmp_path):
    store=SessionStore(tmp_path/"sessions.db")
    sid=store.create(str(tmp_path))
    store.checkpoint(sid,"before edit",{"files":["a.py"]})
    assert store.checkpoints(sid,str(tmp_path))[0]["payload"]=={"files":["a.py"]}
