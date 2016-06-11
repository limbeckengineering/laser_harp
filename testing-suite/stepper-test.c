#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>

#include <pthread.h>

#define BUFF_MAX 255

#define IN  0
#define OUT 1
 
#define LOW  0
#define HIGH 1


#define STEP 44
#define DIR 45

#define MS1 46
#define MS2 47

#define RST 26
#define SLP 27
#define ENABLE 65

int GPIOExport(int pin){

	char buff[BUFF_MAX];
	ssize_t len;
	int fd;

	fd = open("/sys/class/gpio/export", O_WRONLY);
	if(fd == -1){
		fprintf(stderr, "Failed to open export for writing!\n");
		return -1;
	}

	len = snprintf(buff, BUFF_MAX, "%d", pin);
	write(fd, buff, len);
	close(fd);
	return 0;
}

int GPIOUnxport(int pin){
	char buff[BUFF_MAX];
	ssize_t len;
	int fd;

	fd = open("/sys/class/gpio/unexport", O_WRONLY);
	if(fd == -1){
		fprintf(stderr, "Failed to open unexport for writing!\n");
		return -1;
	}

	len = snprintf(buff, BUFF_MAX, "%d", pin);
	write(fd, buff, len);
	close(fd);

	return 0;
}

int setGPIODirection(int pin, int dir){
	char path[BUFF_MAX];
	int fd;

	snprintf(path, BUFF_MAX, "/sys/class/gpio/gpio%d/direction", pin);
	
	fd = open(path, O_WRONLY);
	if(fd == -1){
		fprintf(stderr, "Failed to open export for writing!\n");
		return -1;
	}

	int e;
	if(dir == IN){
		e = write(fd, "in", 2);
	}else{
		e = write(fd, "out", 3);
	}

	if(e == -1){
		return e;
	}

	close(fd);
	return 0;
}

int readGPIO(int pin){
	char path[BUFF_MAX];
	char value_str[3];
	int fd;

	snprintf(path, BUFF_MAX, "/sys/class/gpio/gpio%d/value", pin);
	fd = open(path, O_RDONLY);
	if (fd == -1) {
		fprintf(stderr, "Failed to open gpio value for reading!\n");
		return -1;
	}

	if (read(fd, value_str, 3) == -1) {
		fprintf(stderr, "Failed to read value!\n");
		return -1;
	}
	close(fd);

	return(atoi(value_str));

}

int writeGPIO(int pin, int value){
 
	char path[BUFF_MAX];
	int fd;
 
	snprintf(path, BUFF_MAX, "/sys/class/gpio/gpio%d/value", pin);
	fd = open(path, O_WRONLY);
	if (fd == -1) {
		fprintf(stderr, "Failed to open gpio value for writing!\n");
		return -1;
	}
 
 	int e;

	e = write(fd, value == HIGH ? "1" : "0", 1); 

	if(e == -1){
		fprintf(stderr, "Failed to write value!\n");
		return -1;
	}
 
	close(fd);
	return 0;
}

void stepMotor(){
	writeGPIO(STEP, LOW);
	writeGPIO(STEP, HIGH);
}

void * MotorLoop_CnstRun(void * delay){
	int * v;
	v = (int *) delay;
	while(1){
		stepMotor();
		usleep(*v);
	}
}

void * MotorLoop_DisctStep(void * steps){
	int * v;
	v = (int *) steps;
	for(int i = 0; i < *v; i++){
		stepMotor();
	}
}

int main(int argc, char* argv[]){

	bool disct = true;

	int step_delay = 10;
	int num_steps = 0;

	int e = 0;

	e += GPIOExport(STEP) + GPIOExport(DIR) + GPIOExport(MS2) + GPIOExport(MS1) + GPIOExport(SLP) + GPIOExport(RST) + GPIOExport(ENABLE);

	if(e < 0){
		printf("Failed to export pins");
		return -1;
	}

	usleep(200);

	setGPIODirection(STEP, OUT);
	setGPIODirection(DIR, OUT);

	setGPIODirection(MS1, OUT);
	setGPIODirection(MS2, OUT);

	setGPIODirection(RST, OUT);
	setGPIODirection(SLP, OUT);
	setGPIODirection(ENABLE, OUT);

	usleep(10);

	writeGPIO(ENABLE, HIGH);

	usleep(10);

	writeGPIO(STEP, HIGH);

	usleep(10);

	writeGPIO(ENABLE, LOW);

	usleep(10);

	writeGPIO(DIR, HIGH);

	writeGPIO(MS1, LOW);
	writeGPIO(MS2, HIGH);

	writeGPIO(RST, HIGH);
	writeGPIO(SLP, HIGH);

	int isCloseRequested = 0;

	while(isCloseRequested == 0){
		pthread_t motor_loop;

		int thr_ret;

		if(disct){
			thr_ret = pthread_create(&motor_loop, NULL, MotorLoop_DisctStep, (void *) &num_steps);
		}else{
			thr_ret = pthread_create(&motor_loop, NULL, MotorLoop_CnstRun, (void *) &step_delay);
		}
		
		if(thr_ret){
			fprintf(stderr,"Error - pthread_create() return code: %d\n", thr_ret);
			return -1;

		}

		char input[256];
		printf("Enter Command: ");
		fgets(input, 256, stdin);

		pthread_cancel(motor_loop);
		pthread_join(motor_loop, NULL);

		const char * cmd = strtok(input, " \n");
		const char * value = strtok(NULL, " \n");

		if(strcmp(cmd, "exit") == 0){
			printf("%s\n", "Exit recieved...");
			isCloseRequested = 1;
		}else if(strcmp(cmd, "dir") == 0){
			int in = atoi(value);
			if(in == HIGH){
				writeGPIO(DIR, HIGH);
			}else if(in == LOW){
				writeGPIO(DIR, LOW);
			}else{
				printf("Error: Invlaid input for dir...\n");
			}
		}else if(strcmp(cmd, "step_delay") == 0){
			int in = atoi(value);
			step_delay = in;
		}else if(strcmp(cmd, "num_step") == 0){
			int in = atoi(value);
			num_steps = in;
		}else if(strcmp(cmd, "sleep") == 0){
			int in = atoi(value);
			if(in == HIGH){
				writeGPIO(SLP, HIGH);
			}else if(in == LOW){
				writeGPIO(SLP, LOW);
			}else{
				printf("Error: Invlaid input for sleep...\n");
			}
		}else if(strcmp(cmd, "reset") == 0){
			int in = atoi(value);
			if(in == HIGH){
				writeGPIO(RST, HIGH);
			}else if(in == LOW){
				writeGPIO(RST, LOW);
			}else{
				printf("Error: Invlaid input for reset...\n");
			}
		}else if(strcmp(cmd, "enable") == 0){
			int in = atoi(value);
			if(in == HIGH){
				writeGPIO(ENABLE, HIGH);
			}else if(in == LOW){
				writeGPIO(ENABLE, LOW);
			}else{
				printf("Error: Invlaid input for enable...\n");
			}
		}else if(strcmp(cmd, "step_mode") == 0){
			if(strcmp(value, "discreet") == 0){
				disct = true;
			}else if(strcmp(value, "continuous") == 0){
				disct = false;
			}else{
				printf("Error: Invlaid input for mode...\n");
			}
		}else if(strcmp(cmd, "micro_step") == 0){
			if(strcmp(value, "full") == 0){
				writeGPIO(MS1, 0);
				writeGPIO(MS2, 0);
			}else if(strcmp(value, "half") == 0){
				writeGPIO(MS1, 1);
				writeGPIO(MS2, 0);
			}else if(strcmp(value, "quarter") == 0){
				writeGPIO(MS1, 0);
				writeGPIO(MS2, 1);
			}else if(strcmp(value, "eighth ") == 0){
				writeGPIO(MS1, 1);
				writeGPIO(MS2, 1);
			}else{
				printf("Error: Invalid input for micro_step");
			}
		}

	}

	printf("Running unexport...\n");

	writeGPIO(ENABLE, HIGH);

	GPIOUnxport(STEP);
	GPIOUnxport(DIR);
	GPIOUnxport(MS1);
	GPIOUnxport(MS2);
	//GPIOUnxport(ENABLE);
	GPIOUnxport(SLP);
	GPIOUnxport(RST);

	return 0;
}
