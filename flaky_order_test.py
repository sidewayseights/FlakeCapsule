state={}
def test_A_sets_state():
    state['ready']=True; assert True
def test_B_requires_state():
    assert state.get('ready') is True, 'state not set by test_A'
