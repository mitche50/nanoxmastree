package main

import (
	"encoding/json"
	"flag"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
	"github.com/go-redis/redis"
)

type QueuedRequests struct {
	Address string `json:address`
	Amount  string `json:amount`
}

var addr = flag.String("addr", "localhost:8080", "http service address")

var upgrader = websocket.Upgrader{} // use default options

func xmas(w http.ResponseWriter, r *http.Request) {
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	defer c.Close()

	client := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // no password set
		DB:       0,  // use default DB
	})
	defer client.Close()

	r_data, err := client.LRange("animation", 0, 9).Result()
	if err != nil {
		panic(err)
	}
	print(r_data)

	test_json, _ := json.Marshal(r_data)

	err = c.WriteMessage(websocket.TextMessage, test_json)
	
	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", message)
		err = c.WriteMessage(mt, message)
		if err != nil {
			log.Println("write:", err)
			break
		}
	}
}


func main() {
	flag.Parse()
	log.SetFlags(0)
	http.HandleFunc("/", xmas)
	log.Fatal(http.ListenAndServe(*addr, nil))
}

