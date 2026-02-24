use actix_files as fs;
use actix_web::{get, HttpResponse, Responder};

#[get("/")]
async fn index() -> impl Responder {
    let html = "<!doctype html><html><body><h1>Polygons!</h1><img src=\"/public/static/polygons.jpg\"></body></html>";
    HttpResponse::Ok().body(html)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    use actix_web::{App, HttpServer};

    HttpServer::new(|| {
        App::new()
            .service(index)
            // VULNERABLE LINE: Changed the root directory from "../static" to ".".
            // Setting the root to the current directory ('.') greatly increases the scope
            // of files that could potentially be accessed using path traversal (../).
            .service(fs::Files::new("/public", "."))
    })
    .bind(("127.0.0.1", 8888))?
    .run()
    .await
}