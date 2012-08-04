#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h> 
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <jansson.h>

static const int   BUFFER_SIZE = 2048;
static const char  table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
static const int   BASE64_INPUT_SIZE = 57;

bool isbase64(char c)
{
   return c && strchr(table, c) != NULL;
}

inline char value(char c)
{
   const char *p = strchr(table, c);
   if(p) {
      return p-table;
   } else {
      return 0;
   }
}

int UnBase64(unsigned char *dest, const unsigned char *src, int srclen)
{
   *dest = 0;
   if(*src == 0) 
   {
      return 0;
   }
   unsigned char *p = dest;
   do
   {

      char a = value(src[0]);
      char b = value(src[1]);
      char c = value(src[2]);
      char d = value(src[3]);
      *p++ = (a << 2) | (b >> 4);
      *p++ = (b << 4) | (c >> 2);
      *p++ = (c << 6) | d;
      if(!isbase64(src[1])) 
      {
         p -= 2;
         break;
      } 
      else if(!isbase64(src[2])) 
      {
         p -= 2;
         break;
      } 
      else if(!isbase64(src[3])) 
      {
         p--;
         break;
      }
      src += 4;
      while(*src && (*src == 13 || *src == 10)) src++;
   }
   while(srclen-= 4);
   *p = 0;
   return p-dest;
}

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

int main(int argc, char *argv[])
{
    int sockfd, portno, n;
    struct sockaddr_in serv_addr;
    struct hostent *server;
    char buffer[BUFFER_SIZE];
    
    if (argc < 3) {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    }

    portno = atoi(argv[2]);
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");
    server = gethostbyname(argv[1]);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
         (char *)&serv_addr.sin_addr.s_addr,
         server->h_length);
    serv_addr.sin_port = htons(portno);
    if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
        error("ERROR connecting");
    
    json_t* request = json_pack("{s:s,s:s,s:i}", "jsonrpc", "2.0", "method", "get_all_users", "id", 1);
    char* json_str = json_dumps(request, 0);
    bzero(buffer,BUFFER_SIZE);
    snprintf(buffer, BUFFER_SIZE, "@api %s\x00", json_str);
    n = write(sockfd,buffer,strlen(buffer)+1);
    if (n < 0) 
         error("ERROR writing to socket");
    bzero(buffer,BUFFER_SIZE);
    n = read(sockfd,buffer,BUFFER_SIZE);
    if (n < 0) 
         error("ERROR reading from socket");
    size_t output_length = 0;
    unsigned char result[BUFFER_SIZE];
    output_length = UnBase64(result, (const char *)buffer, strlen(buffer));
    printf("%s\n",result);
    close(sockfd);
    return 0;
}

