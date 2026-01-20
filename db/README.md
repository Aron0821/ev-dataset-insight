# DB

- Prerequisits

```bash
   yarn add @leapfrogtechnology/sync-db
```

- Make migration file:

```bash
   yarn sync-db make create_table_electric_vehicles
```

---

- Migration List

```bash
   yarn sync-db migrate-list
```

- Run migration

```bash
  yarn sync-db synchronize
```

> This is reflected in `__ev_analysis_migrations` table.

- Rollback

```bash
    yarn sync-db migrate:rollback
```
