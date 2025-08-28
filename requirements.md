
## 1) Scope (v1)
**Apps:**
- **accounts**: auth, simple profile (display name, avatar), sign-up page - Done
- **campaigns**: campaign CRUD.
- **characters**: shared Character (players & NPCs) with race, class, notes section for background.
- **sessions**: session records per campaign with free text field to log information on what's happen that session.

## 2) Data Model (minimum viable fields)

### User & Profile
- **User**: Django built‑in.
- **Profile**: `user OneToOne`, `display_name CharField(80)`, `avatar ImageField (nullable)`.

### Campaign
- `name CharField(120)` **required**
- `description TextField (nullable)`
- `dm CharField(120)` (free text; who’s DM)

### Character
- `campaign FK(Campaign, on_delete=CASCADE)`
- `type ChoiceField(PLAYER|NPC)`
- `name CharField(120)` **required**
- `race CharField(80, null=True)`
- `class_ CharField(80, null=True)`
- `background TextField (nullable)` *(for evolving knowledge)*

### Session
- `campaign FK(Campaign)`
- `date DateField (default=today)`
- `summary TextField` *(core of v1)*