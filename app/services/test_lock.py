from flask import redirect, url_for, flash

def ensure_test_unlocked(test):
    if test.is_locked:
        flash("This test has been dispatched and can no longer be edited.", "error")
        return redirect(url_for("admin.edit_test", test_id=test.id))
    return None