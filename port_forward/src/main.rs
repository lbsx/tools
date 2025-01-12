use std::net::SocketAddr;
use tokio::io::{copy};
use tokio::net::{TcpListener, TcpStream};
use std::error::Error;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Local address to listen on, format: host:port
    #[arg(short, long)]
    local_addr: String,

    /// Target address to forward to, format: host:port
    #[arg(short, long)]
    target_addr: String,
}

async fn handle_connection(
    mut incoming: TcpStream,
    target_addr: SocketAddr,
) -> Result<(), Box<dyn Error>> {
    let mut outgoing = TcpStream::connect(target_addr).await?;
    
    let (mut ri, mut wi) = incoming.split();
    let (mut ro, mut wo) = outgoing.split();
    
    tokio::select! {
        result = copy(&mut ri, &mut wo) => {
            if let Err(e) = result {
                eprintln!("Error copying from incoming to outgoing: {}", e);
            }
        },
        result = copy(&mut ro, &mut wi) => {
            if let Err(e) = result {
                eprintln!("Error copying from outgoing to incoming: {}", e);
            }
        },
    };

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    
    let local_addr: SocketAddr = args.local_addr.parse()?;
    let target_addr: SocketAddr = args.target_addr.parse()?;

    let listener = TcpListener::bind(local_addr).await?;
    println!("Listening on: {}, Forwarding to: {}", local_addr, target_addr);

    loop {
        let (incoming, _remote_addr) = listener.accept().await?;
        let target_addr = target_addr;
        tokio::spawn(async move {
            if let Err(e) = handle_connection(incoming, target_addr).await {
                eprintln!("Error handling connection: {}", e);
            }
        });
    }
}