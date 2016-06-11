#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define TSL2591_VISIBLE           (2)       // channel 0 - channel 1
#define TSL2591_INFRARED          (1)       // channel 1
#define TSL2591_FULLSPECTRUM      (0)       // channel 0

#define TSL2591_ADDR              (0x29)
#define TSL2591_READBIT           (0x01)

#define TSL2591_COMMAND_BIT       (0xA0)    // 1010 0000: bits 7 and 5 for 'command normal'
#define TSL2591_CLEAR_INT         (0xE7)
#define TSL2591_TEST_INT          (0xE4)
#define TSL2591_WORD_BIT          (0x20)    // 1 = read/write word (rather than byte)
#define TSL2591_BLOCK_BIT         (0x10)    // 1 = using block read/write

#define TSL2591_ENABLE_POWEROFF   (0x00)
#define TSL2591_ENABLE_POWERON    (0x01)
#define TSL2591_ENABLE_AEN        (0x02)    // ALS Enable. This field activates ALS function. Writing a one activates the ALS. Writing a zero disables the ALS.
#define TSL2591_ENABLE_AIEN       (0x10)    // ALS Interrupt Enable. When asserted permits ALS interrupts to be generated, subject to the persist filter.
#define TSL2591_ENABLE_NPIEN      (0x80)    // No Persist Interrupt Enable. When asserted NP Threshold conditions will generate an interrupt, bypassing the persist filter

using namespace std;

enum
{
  TSL2591_REGISTER_ENABLE             = 0x00,
  TSL2591_REGISTER_CONTROL            = 0x01,
  TSL2591_REGISTER_THRESHOLD_AILTL    = 0x04, // ALS low threshold lower byte
  TSL2591_REGISTER_THRESHOLD_AILTH    = 0x05, // ALS low threshold upper byte
  TSL2591_REGISTER_THRESHOLD_AIHTL    = 0x06, // ALS high threshold lower byte
  TSL2591_REGISTER_THRESHOLD_AIHTH    = 0x07, // ALS high threshold upper byte
  TSL2591_REGISTER_THRESHOLD_NPAILTL  = 0x08, // No Persist ALS low threshold lower byte
  TSL2591_REGISTER_THRESHOLD_NPAILTH  = 0x09, // etc
  TSL2591_REGISTER_THRESHOLD_NPAIHTL  = 0x0A,
  TSL2591_REGISTER_THRESHOLD_NPAIHTH  = 0x0B,
  TSL2591_REGISTER_PERSIST_FILTER     = 0x0C,
  TSL2591_REGISTER_PACKAGE_PID        = 0x11,
  TSL2591_REGISTER_DEVICE_ID          = 0x12,
  TSL2591_REGISTER_DEVICE_STATUS      = 0x13,
  TSL2591_REGISTER_CHAN0_LOW          = 0x14,
  TSL2591_REGISTER_CHAN0_HIGH         = 0x15,
  TSL2591_REGISTER_CHAN1_LOW          = 0x16,
  TSL2591_REGISTER_CHAN1_HIGH         = 0x17
};

int openI2C(char * filename, uint8_t addr){
	int file;
	if((file = open(filename, O_RDWR)) < 0){
		/* Check Error Number */
		perror("Failed to open the i2c bus");
		return 0;
	}

	if(ioctl(file, I2C_SLAVE, addr) < 0){
		printf("Failed to acquire bus access and/or talk to slave.\n");
		return 0;
	}

	return file;
}

int readI2C(int file, int len, unsigned char * buff){
	if(read(file, buff, len) != len){
		printf("Failed to read from i2c bus.\n");
		return -1;
	}
	return 1;
}

int writeI2C(int file, int len, unsigned char * buff){
	if(write(file, buff, len) != len){
		printf("Failed to write to i2c bus.\n");
		return -1;
	}
	return 1;
}

uint8_t read8(int file, uint8_t addr){
	writeI2C(file, 1, &addr);
	usleep(10);
	uint8_t recv;
	readI2C(file, 1, &recv);
	return recv;
}

uint16_t read16(int file, uint8_t addr){
	writeI2C(file, 1, &addr);
	usleep(10);
	uint16_t recv;
	readI2C(file, 2, &recv);
	return recv;
}

int write8(int file, uint8_t addr, uint8_t send){
	int e = 0;
	e += writeI2C(file, 1, &addr);
	usleep(10);
	e += writeI2C(file, 1, &send);
	return e;
}

int write16(int file, uint8_t addr, uint16_t send){
	int e = 0;
	e += writeI2C(file, 1, &addr);
	usleep(10);
	e += writeI2C(file, 2, &send);
	return e;
}

int main(int argc, char *argv[]){

	int file = openI2C("/dev/i2c-3", 0x29);

	uint8_t id = read8(file, TSL2591_COMMAND_BIT | TSL2591_REGISTER_DEVICE_ID);

	cout << id << endl;

}