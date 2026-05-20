use pyo3_stub_gen::Result;
use std::fs;
use std::path::Path;

/// pyo3-stub-gen mixed layout writes `python/allegro/allegro/__init__.pyi`; maturin expects
/// `python/allegro/allegro.pyi` for the extension module.
fn relocate_extension_stub(project_root: &Path) -> std::io::Result<()> {
    let nested = project_root.join("python/allegro/allegro/__init__.pyi");
    let flat = project_root.join("python/allegro/allegro.pyi");
    if nested.exists() {
        if flat.exists() {
            fs::remove_file(&flat)?;
        }
        if let Some(parent) = flat.parent() {
            fs::create_dir_all(parent)?;
        }
        fs::rename(&nested, &flat)?;
        if let Ok(mut entries) = fs::read_dir(project_root.join("python/allegro/allegro"))
            && entries.next().is_none()
        {
            let _ = fs::remove_dir(project_root.join("python/allegro/allegro"));
        }
    }
    Ok(())
}

fn main() -> Result<()> {
    let project_root = Path::new(env!("CARGO_MANIFEST_DIR"));
    allegro::stub_info()?.generate()?;
    relocate_extension_stub(project_root)?;
    Ok(())
}
