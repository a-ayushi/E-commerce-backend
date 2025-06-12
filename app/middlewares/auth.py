from fastapi import Depends, HTTPException, status

def get_current_admin_user():
    # Simulate RBAC
    user = {"role": "admin"}
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user
