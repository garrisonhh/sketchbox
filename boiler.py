import pygame as pg

def main():
	pg.init()
	screen = pg.display.set_mode((640, 480))

	while 1:
		for e in pg.event.get():
			if e.type == pg.QUIT:
				pg.quit()
				exit(0)

		screen.fill((0, 0, 0))
		pg.display.flip()

if __name__ == "__main__":
	main()
