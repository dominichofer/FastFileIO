/// Format size in bytes to KiB, MiB, or GiB
pub fn format_bytes(value: u64) -> String {
    if value >= 1024_u64.pow(3) {
        let gib = value / 1024_u64.pow(3);
        format!("{} GiB", format_with_separator(gib))
    } else if value >= 1024_u64.pow(2) {
        let mib = value / 1024_u64.pow(2);
        format!("{} MiB", format_with_separator(mib))
    } else if value >= 1024 {
        let kib = value / 1024;
        format!("{} KiB", format_with_separator(kib))
    } else {
        format!("{} B", format_with_separator(value))
    }
}

fn format_with_separator(value: u64) -> String {
    let formatted = value.to_string();
    let chars: Vec<char> = formatted.chars().collect();
    let len = chars.len();
    let mut result = String::new();
    for (i, c) in chars.iter().enumerate() {
        if i > 0 && (len - i) % 3 == 0 {
            result.push('\'');
        }
        result.push(*c);
    }
    result
}

/// Format bandwidth in MiB/s
pub fn format_mib_per_s(value: f64) -> String {
    if value >= 1024.0 {
        let gib_per_s = value / 1024.0;
        format!("{:.2} GiB/s", gib_per_s)
    } else {
        format!("{:.2} MiB/s", value)
    }
}
