---
name: alembic-migration
description: Generate and manage Alembic database migrations for Qasyp App. Use when adding a new model, changing a column, adding an index, or running migrations in any environment. Encodes safe migration practices to protect production data.
---

# Alembic Migration

Generate and manage database schema migrations using Alembic for Qasyp App's PostgreSQL database.

## When to Use

- A new SQLAlchemy model has been added
- An existing model has a new, removed, or modified column
- A new index or constraint needs to be added
- Running migrations in development, staging, or production
- Reviewing or rolling back a migration

---

## Project Setup

Alembic is configured at the project root:

```
alembic/
  env.py              # async SQLAlchemy setup
  versions/           # migration files live here
alembic.ini           # points to DATABASE_URL from env
```

### alembic.ini (key setting)

```ini
script_location = alembic
sqlalchemy.url = %(DATABASE_URL)s
```

### env.py (async pattern)

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.db.base import Base
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(config.get_section(config.config_ini_section))
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

---

## Creating a Migration

### Step 1 — Make your model changes

Edit the SQLAlchemy model in `app/models/`. Example: adding a `vat_certificate_number` column:

```python
class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bin: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    vat_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    vat_certificate_number: Mapped[str | None] = mapped_column(String(50), nullable=True)  # new
```

### Step 2 — Auto-generate the migration

```bash
docker compose exec api alembic revision --autogenerate -m "add_vat_certificate_number_to_business_profiles"
```

This creates a new file in `alembic/versions/`. Always review it before running.

### Step 3 — Review the generated file

```python
# Example generated migration
def upgrade() -> None:
    op.add_column(
        "business_profiles",
        sa.Column("vat_certificate_number", sa.String(50), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("business_profiles", "vat_certificate_number")
```

Check for:
- [ ] `upgrade()` does exactly what the model change requires — nothing more
- [ ] `downgrade()` is the correct inverse of `upgrade()`
- [ ] No accidental table drops or column drops from unrelated models
- [ ] New non-nullable columns have a `server_default` or the table is empty in production

### Step 4 — Run the migration

```bash
# Development
docker compose exec api alembic upgrade head

# Check current revision
docker compose exec api alembic current

# View migration history
docker compose exec api alembic history --verbose
```

---

## Migration Naming Convention

```
{short_description_of_change}

Examples:
add_vat_certificate_number_to_business_profiles
create_profile_embeddings_table
add_index_on_business_profiles_bin
add_match_score_to_match_results
rename_industry_field_to_industry_sector
```

Use lowercase with underscores. Be specific — the name should tell you exactly what changed.

---

## Safe Migration Rules

### Never drop a column directly in production

Dropping a column while the application is still referencing it causes errors. Use a two-step approach:

**Step 1** — Remove all references to the column in code and deploy.
**Step 2** — In the next release, create a migration to drop the column.

```python
# Safe drop — only after code references are removed
def upgrade() -> None:
    op.drop_column("business_profiles", "old_field_name")
```

### Non-nullable columns require a default

If adding a non-nullable column to a table that already has rows:

```python
def upgrade() -> None:
    # Add as nullable first
    op.add_column("business_profiles", sa.Column("new_field", sa.String(100), nullable=True))
    # Backfill existing rows
    op.execute("UPDATE business_profiles SET new_field = 'default_value' WHERE new_field IS NULL")
    # Then make it non-nullable
    op.alter_column("business_profiles", "new_field", nullable=False)
```

### Always include `downgrade()`

Every migration must have a working `downgrade()` function. Never use `pass` in `downgrade()`.

---

## Adding Indexes

```python
def upgrade() -> None:
    op.create_index(
        "ix_business_profiles_bin",
        "business_profiles",
        ["bin"],
        unique=True,
    )
    op.create_index(
        "ix_profile_embeddings_profile_id",
        "profile_embeddings",
        ["profile_id"],
    )

def downgrade() -> None:
    op.drop_index("ix_profile_embeddings_profile_id", table_name="profile_embeddings")
    op.drop_index("ix_business_profiles_bin", table_name="business_profiles")
```

---

## Rolling Back

```bash
# Roll back the most recent migration
docker compose exec api alembic downgrade -1

# Roll back to a specific revision
docker compose exec api alembic downgrade {revision_id}

# Roll back everything (development only — never in production)
docker compose exec api alembic downgrade base
```

---

## Running in Staging and Production

```bash
# Always run a dry-run check first
alembic upgrade head --sql   # prints the SQL without executing

# Apply to staging
DATABASE_URL=<staging-url> alembic upgrade head

# Apply to production
DATABASE_URL=<production-url> alembic upgrade head
```

**Before running in production:**
- [ ] Migration reviewed and approved by both developers
- [ ] `downgrade()` tested in staging
- [ ] Database backup taken
- [ ] Migration run during low-traffic window if it involves large table changes
- [ ] Application deployed immediately after migration (keep schema and code in sync)

---

## Checklist

For every migration before committing:

- [ ] File name clearly describes the change
- [ ] `upgrade()` matches the model change exactly
- [ ] `downgrade()` is the correct inverse — not `pass`
- [ ] Non-nullable column additions include a backfill step
- [ ] Column drops follow the two-step deprecation pattern
- [ ] Migration tested locally with `alembic upgrade head` and `alembic downgrade -1`
- [ ] No accidental changes to unrelated tables in the generated file
