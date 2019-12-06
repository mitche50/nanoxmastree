package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/go-redis/redis"
	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
)

func init() {
	// loads values from .env into the system
	if err := godotenv.Load(); err != nil {
		log.Print("No .env file found")
	}
}

func sendBalance(c *websocket.Conn, client *redis.Client) {
	// sends the balance to the provided websocket
	balance, _ := client.Get("donations").Result()
	balanceMessage := make(map[string]string)
	balanceMessage["balance"] = balance
	balanceJSON, _ := json.Marshal(balanceMessage)
	err := c.WriteMessage(websocket.TextMessage, []byte(balanceJSON))
	if err != nil {
		log.Print("websocket error:", err)
	}
	return
}

func xmas(w http.ResponseWriter, r *http.Request) {
	var upgrader = websocket.Upgrader{} // use default options
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	defer c.Close()

	redisHost, exists := os.LookupEnv("REDIS_HOST")
	if !exists {
		redisHost = "localhost"
	}
	redisPort, exists := os.LookupEnv("REDIS_PORT")
	if !exists {
		redisPort = "6379"
	}
	redisPW, exists := os.LookupEnv("REDIS_PW")
	if !exists {
		redisPW = ""
	}

	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%v:%v", redisHost, redisPort),
		Password: fmt.Sprintf("%v", redisPW), // no password set
		DB:       0,                          // use default DB
	})
	defer client.Close()

	go func() {
		p := client.Subscribe("PendingAnimations", "AnimationProcessing", "AnimationCompleted")
		fmt.Println("in goroutine")
		for {
			msg, err := p.ReceiveMessage()
			if err != nil {
				break
			}

			fmt.Println(msg.Channel, msg.Payload)
			switch msg.Channel {
			case "AnimationProcessing":
				fmt.Println(msg.Channel, msg.Payload)
				wsData, _ := json.Marshal(msg.Payload)
				sendBalance(c, client)
				err = c.WriteMessage(websocket.TextMessage, wsData)
			case "PendingAnimations":
				err = c.WriteMessage(websocket.TextMessage, []byte(msg.Payload))
			case "AnimationCompleted":
				err = c.WriteMessage(websocket.TextMessage, []byte("done"))
			}
		}
	}()

	rData, err := client.LRange("animations", 0, 9).Result()
	if err != nil {
		panic(err)
	}
	print(rData)

	testJSON, _ := json.Marshal(rData)

	err = c.WriteMessage(websocket.TextMessage, testJSON)
	sendBalance(c, client)

	for {
		_, message, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", message)
	}
}

func main() {

	var addr = flag.String("addr", "localhost:2512", "http service address")

	flag.Parse()
	log.SetFlags(0)

	http.HandleFunc("/", xmas)
	log.Fatal(http.ListenAndServe(*addr, nil))
}
