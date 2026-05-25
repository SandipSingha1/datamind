@echo off
echo ========================================
echo Running dbt compile and run
echo ========================================

cd dbt_project

echo.
echo Step 1: Compiling dbt models...
dbt compile --profiles-dir .

echo.
echo Step 2: Running dbt models...
dbt run --profiles-dir .

echo.
echo Step 3: Testing dbt models...
dbt test --profiles-dir .

echo.
echo ========================================
echo dbt execution complete!
echo ========================================
echo.
echo Next steps:
echo 1. Check target/manifest.json was created
echo 2. Run ingestion: cd datamind_knowledge_svc ^&^& python ingestion.py ../dbt_project/target/manifest.json
echo 3. Start services
pause

@REM Made with Bob
