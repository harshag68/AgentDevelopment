      </style>
    </head>
    <body>
      <h1>{title}</h1>
      <h3>Contexto</h3>
      <p>{context}</p>
      <h3>Requerimientos</h3>
      <p>{requirements}</p>
      <h3>Permisos</h3>
      <p>{permissions}</p>
      <h3>Outputs</h3>
      <p>{outputs}</p>
      <hr />
      {html_steps}
    </body>
    </html>
    """
    return html.strip()


def init_db():
    """En modo GCP asumimos que las tablas ya existen."""
    print(">>> [manual_store_gcp] init_db (no-op, usando BigQuery)")
    return


def save_manual(manual_struct: dict) -> dict:
    print(">>> [manual_store_gcp] save_manual INICIO")

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    manual_id = manual_struct.get("manual_id") or f"MAN-{uuid.uuid4().hex[:10]}"
    version = manual_struct.get("version") or 1

    # keywords: ensure list
    keywords = manual_struct.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    # 1) Render HTML and upload to GCS
    html = _render_manual_html(manual_struct)
    blob_path = f"manuals/{manual_id}/v{version}.html"
    blob = bucket.blob(blob_path)

    print(f">>> [manual_store_gcp] Subiendo HTML a gs://{MANUALS_BUCKET}/{blob_path}")
    blob.upload_from_string(html, content_type="text/html")
    gcs_uri = f"gs://{MANUALS_BUCKET}/{blob_path}"
    print(">>> [manual_store_gcp] HTML subido OK:", gcs_uri)

    # 2) manuals_dict row
    manuals_row = {
        "manual_id": manual_id,
        "title": manual_struct.get("title"),
        "business_area": manual_struct.get("business_area"),
        "requester": manual_struct.get("requester"),
        "created_by": manual_struct.get("created_by") or "manual-ai",
        "created_at": manual_struct.get("created_at") or now_str,
        "last_updated": now_str,
        "context": manual_struct.get("context"),
        "requirements": manual_struct.get("requirements"),
        "permissions": manual_struct.get("permissions"),
        "outputs": manual_struct.get("outputs"),
        "keywords": keywords,  # ARRAY<STRING>
    }

    print(">>> [manual_store_gcp] Insertando en manuals_dict ...")
    errors = bq_client.insert_rows_json(MANUALS_TABLE, [manuals_row])
    if errors:
        print("!!! [manual_store_gcp] ERROR manuals_dict:", errors)
        raise RuntimeError(f"Error insertando en manuals_dict: {errors}")
    print(">>> [manual_store_gcp] OK manuals_dict")

    # 3) steps row
    steps = manual_struct.get("steps", [])
    step_rows = []
    for idx, step in enumerate(steps, start=1):
        step_rows.append(
            {
                "manual_id": manual_id,
                "step_number": step.get("step_number", idx),
                "step_title": step.get("step_title"),
                "step_description": step.get("step_description"),
                "expected_output": step.get("expected_output"),
                "required_tools": step.get("required_tools"),
                "estimated_time": step.get("estimated_time"),
                "is_critical": bool(step.get("is_critical")),
            }
        )

    if step_rows:
        print(">>> [manual_store_gcp] Insertando en manual_steps ...")
        errors = bq_client.insert_rows_json(STEPS_TABLE, step_rows)
        if errors:
            print("!!! [manual_store_gcp] ERROR manual_steps:", errors)
            raise RuntimeError(f"Error insertando en manual_steps: {errors}")
        print(">>> [manual_store_gcp] OK manual_steps")

    # 4) files row
    files_row = {
        "manual_id": manual_id,
        "version": version,
        "file_path": gcs_uri,
        "format": "html",
        "created_at": now_str,
        "created_by": manuals_row["created_by"],
    }

    print(">>> [manual_store_gcp] Insertando en manual_files ...")
    errors = bq_client.insert_rows_json(FILES_TABLE, [files_row])
    if errors:
        print("!!! [manual_store_gcp] ERROR manual_files:", errors)
        raise RuntimeError(f"Error insertando en manual_files: {errors}")
    print(">>> [manual_store_gcp] OK manual_files")

    result = {
        "manual_id": manual_id,
        "title": manuals_row["title"],
        "business_area": manuals_row["business_area"],
        "requester": manuals_row["requester"],
        "created_by": manuals_row["created_by"],
        "created_at": manuals_row["created_at"],
        "last_updated": manuals_row["last_updated"],
        "steps_count": len(steps),
        "file_path": gcs_uri,
        "version": version,
    }

    print(">>> [manual_store_gcp] save_manual FIN OK:", manual_id)
    return result


def search_manuals(query: str = "") -> List[Dict]:
    """
    Busca manuales en BigQuery.
    - Si query == "" -> trae hasta 50 manuales ordenados por last_updated DESC.
    - Si query tiene texto -> filtra por título, contexto, outputs y keywords.
    """
    q = (query or "").strip().lower()

    print("\n[manual_store_gcp] search_manuals() llamado")
    print("  PROJECT_ID:", PROJECT_ID)
    print("  DATASET   :", BQ_DATASET)
    print("  TABLE     :", MANUALS_TABLE)
    print("  query_txt :", repr(q))

    try:
        if not q:
            # No filter: same behavior as test_raw
            sql = f"""
              SELECT
                manual_id,
                title,
                business_area,
                requester,
                created_at,
                last_updated,
                keywords
              FROM `{MANUALS_TABLE}`
              ORDER BY last_updated DESC
              LIMIT 50
            """
            print("  SQL (sin filtro):")
            print(sql)
            job = bq_client.query(sql)

        else:
            # With text filter (in title, context, outputs or keywords)
            sql = f"""
              SELECT
                manual_id,
                title,
                business_area,
                requester,
                created_at,
                last_updated,
                keywords
              FROM `{MANUALS_TABLE}`
              WHERE (
                LOWER(title)   LIKE '%' || @q || '%' OR
                LOWER(context) LIKE '%' || @q || '%' OR
                LOWER(outputs) LIKE '%' || @q || '%' OR
                EXISTS (
                  SELECT kw
                  FROM UNNEST(keywords) kw
                  WHERE LOWER(kw) LIKE '%' || @q || '%'
                )
              )
              ORDER BY last_updated DESC
              LIMIT 50
            """
            print("  SQL (con filtro):")
            print(sql)
            job = bq_client.query(
                sql,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("q", "STRING", q),
                    ]
                ),
            )

        rows = list(job.result())
        print("  filas devueltas por BQ:", len(rows))

        results: List[Dict] = []
        for r in rows:
            results.append(
                {
                    "manual_id": r.manual_id,
                    "title": r.title,
                    "business_area": getattr(r, "business_area", None),
                    "requester": getattr(r, "requester", None),
                    "created_at": str(getattr(r, "created_at", "")),
                    "last_updated": str(getattr(r, "last_updated", "")),
                    "keywords": list(getattr(r, "keywords", []) or []),
                }
            )

        print("  resultados procesados:", len(results))
        print("-------------------------------------------------\n")
        return results

    except Exception as e:
        print("!!! ERROR en search_manuals:", repr(e))
        print("-------------------------------------------------\n")
        # Always return list, never None
        return []



def get_manual(manual_id: str) -> dict | None:
    # 1) metadata
    meta_job = bq_client.query(
        f"SELECT * FROM `{MANUALS_TABLE}` WHERE manual_id = @manual_id",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("manual_id", "STRING", manual_id)
            ]
        ),
    )
    meta_rows = list(meta_job.result())
    if not meta_rows:
        return None
    m = meta_rows[0]

    # 2) steps
    steps_job = bq_client.query(
        f"""
        SELECT *
        FROM `{STEPS_TABLE}`
        WHERE manual_id = @manual_id
        ORDER BY step_number
        """,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("manual_id", "STRING", manual_id)
            ]
        ),
    )
    steps = []
    for s in steps_job.result():
        steps.append(
            {
                "step_number": s.step_number,
                "step_title": s.step_title,
                "step_description": s.step_description,
                "expected_output": s.expected_output,
                "required_tools": s.required_tools,
                "estimated_time": s.estimated_time,
                "is_critical": s.is_critical,
            }
        )

    # 3) files
    files_job = bq_client.query(
        f"""
        SELECT *
        FROM `{FILES_TABLE}`
        WHERE manual_id = @manual_id
        ORDER BY version DESC
        """,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("manual_id", "STRING", manual_id)
            ]
        ),
    )
    files = []
    for f in files_job.result():
        files.append(
            {
                "version": f.version,
                "file_path": f.file_path,
                "format": f.format,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "created_by": f.created_by,
            }
        )

    return {
        "manual_id": m.manual_id,
        "title": m.title,
        "business_area": m.business_area,
        "requester": m.requester,
        "created_by": m.created_by,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "last_updated": m.last_updated.isoformat() if m.last_updated else None,
        "context": m.context,
        "requirements": m.requirements,
        "permissions": m.permissions,
        "outputs": m.outputs,
        "keywords": list(m.keywords) if m.keywords else [],
        "steps": steps,
        "files": files,
    }
