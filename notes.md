## 5th nov notes

is it so that if it's a many to one relation. does that always mean the the table with many will have the foreign key?
Yes. In a relational database, for a one-to-many (1:N) relationship, the foreign key is placed in the table on the "many" side.
11:50 PM
the adjoining for many to many relationship is called Junction table

## for future

what if different policiy leaves

does leaves_track employee have many to many

## questions releated

venv ? why we need this
what is this query? When to use this type of queries?

```
WITH RECURSIVE subtree(id, name, manager_id, depth) AS (
    SELECT id, name, manager_id, 0
    FROM employees
    WHERE id = :root_id
  UNION ALL
    SELECT e.id, e.name, e.manager_id, s.depth + 1
    FROM employees e
    JOIN subtree s ON e.manager_id = s.id
    WHERE s.depth < 20
)
SELECT id, name, depth
FROM subtree
WHERE depth > 0
ORDER BY depth, name;
```
