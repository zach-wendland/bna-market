# Deployment Checklist - User Authentication & Saved Features

This checklist ensures all authentication features are properly deployed to Vercel.

## ✅ Pre-Deployment Steps (MUST DO FIRST)

### 1. Apply Database Migration in Supabase
**CRITICAL: Do this BEFORE deploying code, otherwise API endpoints will fail!**

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy the entire contents of `supabase/migrations/001_auth_and_user_features.sql`
6. Paste into the SQL editor
7. Click **Run** (or press Ctrl+Enter)
8. Verify all tables created:
   ```sql
   -- Run this query to verify:
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name IN ('user_profiles', 'user_property_lists', 'user_property_list_items', 'user_saved_searches');
   ```
   - Should return 4 rows

**Expected Output:**
```
user_profiles
user_property_lists
user_property_list_items
user_saved_searches
```

### 2. Configure Supabase Auth Settings

1. In Supabase Dashboard, go to **Authentication** → **Settings**
2. Enable **Email Auth** under Auth Providers
3. Configure **Email Templates** → **Magic Link**:
   - Subject: `Sign in to BNA Market`
   - Body: Include clear call-to-action button
   - Set redirect URL: `{{ .SiteURL }}/auth/callback`
4. Set **Site URL**: `https://bna-market.vercel.app`
5. Add **Redirect URLs** (whitelist):
   - `https://bna-market.vercel.app/auth/callback`
   - `http://localhost:5173/auth/callback` (for local development)

### 3. Verify Supabase Environment Variables in Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Verify these exist (DO NOT CHANGE):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY` (used for JWT verification)
   - `SUPABASE_DB_PASSWORD`

**If missing, get them from Supabase Dashboard → Settings → API**

### 4. Install Backend Dependencies Locally (Test First)

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Verify pyjwt is installed
python -c "import jwt; print(jwt.__version__)"
```

### 5. Test Backend Locally (Optional but Recommended)

```bash
# Start Flask API
python -m bna_market web serve

# In another terminal, test endpoints:
curl http://localhost:5000/api/health
curl http://localhost:5000/api/auth/session
# ^ Should return 401 (expected - not authenticated)
```

## 📦 Deployment Steps

### Step 1: Commit All Changes

```bash
# Stage all files
git add .

# Create commit
git commit -m "feat: add user authentication with magic link, property lists, and saved searches

## Major Features
- Magic link authentication (passwordless login)
- User property lists (create, manage, organize saved properties)
- Saved searches (save filter preferences for quick access)
- Vue Router with auth guards and protected routes
- Row Level Security (RLS) policies in database

## Backend Changes (~1,650 lines)
- Auth middleware: JWT verification decorators
- Auth API: 5 endpoints (magic-link, verify, session, logout, refresh)
- Lists API: 8 endpoints (CRUD for property lists)
- Searches API: 5 endpoints (CRUD for saved searches)
- Database migration: 4 new tables with RLS policies

## Frontend Changes (~2,300 lines)
- Auth store: user/token state management
- Lists store: property lists CRUD operations
- Searches store: filter management and search saving
- Router: 7 routes with auth guards
- Login UI: MagicLinkForm, LoginView, AuthCallbackView
- Updated AppHeader: sign-in button + user menu dropdown
- API client: auth headers + 16 new API functions

## Dependencies
- Backend: pyjwt>=2.8.0
- Frontend: vue-router@^4.2.5 (already installed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### Step 2: Push to Deploy

```bash
# Push to main branch (triggers Vercel deployment)
git push origin main
```

### Step 3: Monitor Deployment

1. Go to Vercel Dashboard → Deployments
2. Watch the build progress
3. Check for errors in build logs
4. Wait for "Ready" status

**Expected Build Time:** 2-5 minutes

## 🧪 Post-Deployment Verification

### 1. Verify API Endpoints

```bash
# Health check (should work)
curl https://bna-market.vercel.app/api/health

# Auth session (should return 401 - expected)
curl https://bna-market.vercel.app/api/auth/session

# Property lists (should return 401 - expected)
curl https://bna-market.vercel.app/api/lists

# Saved searches (should return 401 - expected)
curl https://bna-market.vercel.app/api/searches
```

**Expected Results:**
- `/api/health` → 200 OK with health data
- `/api/auth/session` → 401 with `{"error": "Missing authorization"}`
- `/api/lists` → 401 with `{"error": "Missing authorization"}`
- `/api/searches` → 401 with `{"error": "Missing authorization"}`

### 2. Test Frontend Routing

Visit these URLs directly in browser:
- https://bna-market.vercel.app/ (Dashboard)
- https://bna-market.vercel.app/login (Login page - should work)
- https://bna-market.vercel.app/profile (Should redirect to /login)
- https://bna-market.vercel.app/lists (Should redirect to /login)

### 3. Test Magic Link Login Flow (End-to-End)

1. Go to https://bna-market.vercel.app/login
2. Enter your email address
3. Click "Send magic link"
4. Check your email inbox
5. Click the magic link in email
6. Should redirect to dashboard with user logged in
7. Check AppHeader - should show user menu with email
8. Click user menu → verify "My Lists" and "Profile" links work
9. Click "Sign Out" → should redirect to login page

### 4. Test Protected Routes (After Login)

After successfully logging in:
- Visit `/profile` - should show your user info
- Visit `/lists` - should load (currently empty page - UI not built yet)
- Refresh page - should stay logged in (session persistence)
- Open browser console - check for errors

## 🐛 Troubleshooting

### Build Fails on Vercel

**Error:** `ModuleNotFoundError: No module named 'jwt'`
- **Fix:** Ensure `pyjwt>=2.8.0` is in `pyproject.toml` dependencies (not dev-dependencies)

**Error:** Vue router errors
- **Fix:** Ensure `vue-router@^4.2.5` in `frontend/package.json` dependencies

### Magic Link Not Sending

**Check:**
1. Supabase Dashboard → Authentication → Settings → Email Auth enabled
2. Verify email template configured
3. Check Supabase logs for errors
4. Ensure site URL and redirect URLs are correct

### 401 Errors on Protected Routes

**After login, still getting 401:**
1. Check browser console for JWT token in localStorage
2. Verify token is being sent in Authorization header
3. Check Supabase service key is correct in Vercel env vars
4. Ensure auth middleware is using correct JWT secret

### Database Errors

**Error:** `relation "user_profiles" does not exist`
- **Fix:** Migration not applied - go back to Step 1 and run SQL migration

**Error:** `permission denied for table user_profiles`
- **Fix:** RLS policies not applied - check migration includes all RLS policies

### Frontend Shows Blank Page

1. Open browser DevTools → Console tab
2. Look for JavaScript errors
3. Common issues:
   - Router not registered in main.ts
   - Missing imports
   - Component loading errors

## ✅ Success Criteria

Deployment is successful when:
- [ ] Health endpoint returns 200
- [ ] Auth endpoints return 401 (expected when not authenticated)
- [ ] Login page loads at /login
- [ ] Can send magic link email
- [ ] Can verify magic link and login
- [ ] User menu shows in AppHeader after login
- [ ] Protected routes redirect to login when not authenticated
- [ ] Session persists across page refreshes
- [ ] Sign out works and redirects to login

## 📊 Verification Status

After completing all steps, update this section:

- [ ] Database migration applied
- [ ] Supabase Auth configured
- [ ] Environment variables verified
- [ ] Code committed and pushed
- [ ] Vercel deployment successful
- [ ] API endpoints responding
- [ ] Frontend routing working
- [ ] Magic link login tested
- [ ] Protected routes working
- [ ] Session persistence working

## 🔒 Security Notes

- Magic link emails expire in 1 hour (Supabase default)
- Access tokens expire in 1 hour (can be configured)
- Refresh tokens last 30 days
- RLS policies enforce user data isolation at database level
- JWT tokens are verified server-side with Supabase service key
- Rate limiting applied to auth endpoints (5 magic links/hour, 10 verifications/hour)

## 📚 Next Steps (After Deployment)

1. Create property lists UI components
2. Create saved searches UI components
3. Test full user workflow (login → save properties → save searches)
4. Add toast notifications for user feedback
5. Consider adding Shadcn Vue components (Phase 4)
6. Set up error monitoring (Sentry)
