use actix_files as fs;
use actix_web::{http::StatusCode, test, App};

// This test ensures the fixed server does not disclose files outside the intended static directory
#[actix_web::test]
async fn sensitive_file_is_not_accessible_from_public() {
    // Build the same app as in src/main.rs (public files pointed to ../static in this project)
    let app = test::init_service(App::new().service(fs::Files::new("/public", "static")))
    .await;

    // Attempt to access the sensitive file through the public mount
    let req = test::TestRequest::get()
        .uri("/public/sensitive.txt")
        .to_request();
    let resp = test::call_service(&app, req).await;
    assert!(
        matches!(
            resp.status(),
            StatusCode::NOT_FOUND | StatusCode::FORBIDDEN | StatusCode::BAD_REQUEST
        ),
        "Sensitive file must not be reachable in fixed server (got {})",
        resp.status()
    );
}

// Also verify common traversal patterns are blocked
#[actix_web::test]
async fn traversal_is_blocked() {
    let app = test::init_service(App::new().service(fs::Files::new("/public", "static")))
    .await;

    for path in [
        "/public/../sensitive.txt",
        "/public/%2e%2e/sensitive.txt",           // URL-encoded ".."
        "/public/..%2F/sensitive.txt",           // mixed encoding
        "/public/%2e%2e%2F%2e%2e/sensitive.txt", // double traversal
    ] {
        let req = test::TestRequest::get().uri(path).to_request();
        let resp = test::call_service(&app, req).await;
        assert!(
            matches!(
                resp.status(),
                StatusCode::NOT_FOUND | StatusCode::FORBIDDEN | StatusCode::BAD_REQUEST
            ),
            "{} should be blocked (got {})",
            path,
            resp.status()
        );
    }
}
