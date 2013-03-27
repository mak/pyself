#include <stdio.h>

int main(int argc,char**argv,char**envp){
  char **p;
  puts("Hello From Hell\nargs:");
  for(p = argv;*p;p++)
    puts(*p);
  puts("env:");
  for(p = envp;*p;p++)
    puts(*p);

  return 0;
}
