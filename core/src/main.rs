//the antivirus engine in currently not functional: it's just scanning files for now.
//we achieved a nice result by obtaining a fast scanner which will be used on our real antivirus system.
use std::fs;
use std::path::Path;
use sha2::{Sha256, Digest};
use walkdir::WalkDir;

fn hash_file(path: &Path) -> Option<String> {
    let data = fs::read(path).ok()?;
    let mut hasher = Sha256::new();
    hasher.update(&data);
    Some(format!("{:x}", hasher.finalize()))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let default = String::from("/Users");
    let target = args.get(1).unwrap_or(&default);

    let mut total = 0;
    let mut scanned = 0;

    // Count total files first (for percentage)
    for entry in WalkDir::new(target).into_iter().filter_map(|e| e.ok()) {
        if entry.path().is_file() {
            total += 1;
        }
    }

    println!("#TOTAL {}", total);

    for entry in WalkDir::new(target).into_iter().filter_map(|e| e.ok()) {
        if entry.path().is_file() {
            scanned += 1;
            if let Some(_) = hash_file(entry.path()) {
                println!("#PROGRESS {} {}", scanned, entry.path().display());
            }
        }
    }

    println!("#DONE {}", scanned);
}