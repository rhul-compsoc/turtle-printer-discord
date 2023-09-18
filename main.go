package main

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"os"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		fmt.Println("Failed to load .env")
	}

	// Start Discord instance
	discord, err := discordgo.New("Bot " + os.Getenv("DISCORD_TOKEN"))
	if err != nil {
		fmt.Println(err)
	}
	defer discord.Close()

	// Start server to listen for incoming connections
	server, err := net.Listen("tcp", ":4444")
	if err != nil {
		fmt.Println(err)
	}
	defer server.Close()

	// Continuously accept incoming connections
	for {
		conn, err := server.Accept()
		if err != nil {
			fmt.Println(err)
		} else {
			fmt.Println("New client connected: " + conn.RemoteAddr().String())
			// Handle client
			go handleClient(discord, conn)
		}
	}
}

func handleClient(discord *discordgo.Session, conn net.Conn) {
	// Create reader to read from connection
	r := bufio.NewReader(conn)
	// Read out image size
	n := readInt(r)
	// Read image
	imgBuf := make([]byte, n)
	_, err := io.ReadFull(r, imgBuf)
	if err != nil {
		fmt.Println(err)
	}
	// Read author name length
	n = readInt(r)
	// Read author name
	authorBuf := make([]byte, n)
	_, err = io.ReadFull(r, authorBuf)
	if err != nil {
		fmt.Println(err)
	}

	fmt.Printf("Received %d bytes from %s", len(imgBuf), string(authorBuf))

	// Send data to Discord
	discord.ChannelMessageSendComplex(os.Getenv("DISCORD_CHANNEL"), &discordgo.MessageSend{
		Embeds: []*discordgo.MessageEmbed{
			{
				Title: fmt.Sprintf("by %s", string(authorBuf)),
			},
		},
		Files: []*discordgo.File{
			{
				Name:        "turtle-drawing.png",
				ContentType: "image/png",
				Reader:      bytes.NewReader(imgBuf),
			},
		},
	})

	conn.Close()
}

// Read int reads 4 bytes from the reader given and returns the integer they represent
func readInt(r *bufio.Reader) int {
	buf := make([]byte, 4)
	_, err := io.ReadFull(r, buf)
	if err != nil {
		fmt.Println(err)
	}
	return int(binary.BigEndian.Uint32(buf))
}
