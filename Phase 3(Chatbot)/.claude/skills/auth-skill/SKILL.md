---
name: auth-skill
description: Handle authentication flows including signup, signin, password security, JWT tokens, and Better Auth integration for full-stack applications.
---

# Auth Skill – Authentication & Authorization

## Instructions
1. **User Signup**
   - Validate user input (email, password, name)
   - Enforce strong password rules
   - Hash passwords using secure algorithms (e.g., bcrypt, argon2)
   - Prevent duplicate accounts
2. **User Signin**
   - Verify credentials securely
   - Protect against timing attacks
   - Return consistent error messages
3. **Password Security**
   - Never store plaintext passwords
   - Use salted password hashing
   - Support password updates and resets (if specified)
4. **JWT Token Handling**
   - Issue JWT tokens on successful authentication
   - Include essential claims (user_id, email, expiration)
   - Configure token expiry and rotation
   - Verify JWT signatures using a shared secret
5. **Better Auth Integration**
   - Configure Better Auth to enable JWT issuance
   - Share `BETTER_AUTH_SECRET` across frontend and backend
   - Attach JWT tokens to API requests via Authorization headers
   - Decode and validate tokens in backend services

## Security & Validation Rules
- Always validate input data using schemas
- Reject invalid or expired tokens with `401 Unauthorized`
- Enforce authorization checks on every protected route
- Never trust client-provided user identifiers without JWT verification
- Ensure logout or token expiry invalidates access

## Best Practices
- Use HTTPS in all environments
- Keep JWT expiration reasonably short (e.g., 7 days)
- Store secrets in environment variables only
- Avoid leaking authentication errors
- Log authentication events securely (no sensitive data)

## Example Flow
```text
User signs up → Password hashed → Account created
User signs in → Credentials verified → JWT issued
Frontend stores session → Sends JWT in API requests
Backend verifies JWT → Identifies user → Authorizes request
