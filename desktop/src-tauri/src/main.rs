// OpenAgent 桌面客户端入口
// Tauri 2.x + Rust backend
//
// 支持三种模式:
// - localhost: 本地 Docker 沙箱
// - cascade: Windsurf 集成模式
// - cloud: 远程云端服务器

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct SessionInfo {
    id: String,
    title: String,
    status: String,
    mode: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AppConfig {
    api_url: String,
    mode: String, // localhost | cascade | cloud
    language: String,
    theme: String,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            api_url: "http://localhost:8000".to_string(),
            mode: "localhost".to_string(),
            language: "zh".to_string(),
            theme: "dark".to_string(),
        }
    }
}

/// 获取应用配置
#[tauri::command]
fn get_config() -> AppConfig {
    AppConfig::default()
}

/// 获取平台信息
#[tauri::command]
fn get_platform_info() -> serde_json::Value {
    serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "family": std::env::consts::FAMILY,
    })
}

/// 检查后端健康状态
#[tauri::command]
async fn check_health(api_url: String) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get(format!("{}/health", api_url))
        .send()
        .await
        .map_err(|e| format!("连接失败: {}", e))?;
    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析失败: {}", e))?;
    Ok(body)
}

/// 创建新会话
#[tauri::command]
async fn create_session(
    api_url: String,
    title: String,
    mode: String,
    model: String,
    prompt: String,
) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/api/sessions/", api_url))
        .json(&serde_json::json!({
            "title": title,
            "mode": mode,
            "model": model,
            "prompt": prompt,
        }))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析失败: {}", e))?;
    Ok(body)
}

/// 获取会话列表
#[tauri::command]
async fn list_sessions(api_url: String) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get(format!("{}/api/sessions/", api_url))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析失败: {}", e))?;
    Ok(body)
}

/// 发送消息到会话
#[tauri::command]
async fn send_message(
    api_url: String,
    session_id: String,
    content: String,
) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/api/sessions/{}/message", api_url, session_id))
        .json(&serde_json::json!({
            "content": content,
            "role": "user",
        }))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析失败: {}", e))?;
    Ok(body)
}

/// 执行交接 (localhost <-> cloud)
#[tauri::command]
async fn handoff_session(
    api_url: String,
    session_id: String,
    target_mode: String,
) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!(
            "{}/api/sessions/{}/handoff",
            api_url, session_id
        ))
        .json(&serde_json::json!({
            "target_mode": target_mode,
        }))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析失败: {}", e))?;
    Ok(body)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_config,
            get_platform_info,
            check_health,
            create_session,
            list_sessions,
            send_message,
            handoff_session,
        ])
        .run(tauri::generate_context!())
        .expect("启动 OpenAgent 桌面客户端失败");
}
