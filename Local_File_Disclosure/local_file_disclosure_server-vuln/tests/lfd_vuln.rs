use actix_files as fs;
use actix_web::{http::StatusCode, test, App};

// This test demonstrates the local file disclosure vulnerability in the vulnerable server
// where the static files root is set to the current directory (".").
#[actix_web::test]
async fn sensitive_file_is_accessible_from_public() {
    // Build the same app as in src/main.rs but we only need the static files service
    let app = test::init_service(
        App::new().service(fs::Files::new("/public", ".")),
    )
    .await;

    // Request the sensitive file directly via the public files mount
    let req = test::TestRequest::get()
        .uri("/public/sensitive.txt")
        .to_request();
    let resp = test::call_service(&app, req).await;

    assert_eq!(resp.status(), StatusCode::OK, "Sensitive file should be reachable in vulnerable server");

    let body_bytes = test::read_body(resp).await;
    let expected = std::fs::read("sensitive.txt").expect("read sensitive.txt");

    assert_eq!(body_bytes.as_ref(), expected.as_slice(), "Leaked content must match file contents");
}
