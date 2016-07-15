#include <stdio.h>
#include <string.h>
int main (int argc ,char ** argv)
{
if ( argc == 3 ) 
{
char* pid=argv[1];
char* dir=argv[2];
FILE *p;
char cmd[32];
p = fopen("/tmp/gdb_cmds", "w");
fprintf(p, "file /proc/%s/exe\ncall chdir(\"%s\")\ndetach\nquit\n", pid, dir);
fclose(p);
sprintf(cmd, "gdb -p %s -batch -x /tmp/gdb_cmds", pid);
system(cmd);
}
else
 {
  printf("Need a pid argument");
}
return 0;
}
