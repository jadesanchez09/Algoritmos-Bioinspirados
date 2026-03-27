import random

# Reproducible results
random.seed(42)

# Objective function to minimize
def objective_function(position):
    x = position[0]
    y = position[1]
    return x**2 + y**2

# Particle class
class Particle:
    def __init__(self, bounds):
        # Random initial position
        self.position = [
            random.uniform(bounds[0][0], bounds[0][1]),
            random.uniform(bounds[1][0], bounds[1][1])
        ]

        # Random initial velocity
        self.velocity = [
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ]

        # Personal best position starts as current position
        self.best_position = self.position[:]
        self.best_value = objective_function(self.position)

    def update_velocity(self, global_best_position, w, c1, c2):
        for i in range(len(self.velocity)):
            r1 = random.random()
            r2 = random.random()

            cognitive = c1 * r1 * (self.best_position[i] - self.position[i])
            social = c2 * r2 * (global_best_position[i] - self.position[i])

            self.velocity[i] = w * self.velocity[i] + cognitive + social

    def update_position(self, bounds):
        for i in range(len(self.position)):
            self.position[i] += self.velocity[i]

            # Keep particle inside bounds
            if self.position[i] < bounds[i][0]:
                self.position[i] = bounds[i][0]
            elif self.position[i] > bounds[i][1]:
                self.position[i] = bounds[i][1]

    def evaluate(self):
        current_value = objective_function(self.position)

        # Update personal best if current position is better
        if current_value < self.best_value:
            self.best_value = current_value
            self.best_position = self.position[:]

# PSO class
class PSO:
    def __init__(self, num_particles, num_iterations, bounds, w=0.5, c1=1.5, c2=1.5):
        self.num_particles = num_particles
        self.num_iterations = num_iterations
        self.bounds = bounds
        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.swarm = [Particle(bounds) for _ in range(num_particles)]

        # Initialize global best
        self.global_best_position = self.swarm[0].position[:]
        self.global_best_value = objective_function(self.global_best_position)

    def run(self):
        for iteration in range(self.num_iterations):
            for particle in self.swarm:
                particle.evaluate()

                # Update global best
                if particle.best_value < self.global_best_value:
                    self.global_best_value = particle.best_value
                    self.global_best_position = particle.best_position[:]

            for particle in self.swarm:
                particle.update_velocity(
                    self.global_best_position,
                    self.w,
                    self.c1,
                    self.c2
                )
                particle.update_position(self.bounds)

            print(
                f"Iteration {iteration + 1:02d} | "
                f"Global Best Position = {self.global_best_position} | "
                f"Global Best Value = {self.global_best_value:.6f}"
            )

        return self.global_best_position, self.global_best_value

# Search bounds for x and y
bounds = [(-10, 10), (-10, 10)]

# Run PSO
pso = PSO(
    num_particles=5,
    num_iterations=20,
    bounds=bounds,
    w=0.5,
    c1=1.5,
    c2=1.5
)

best_position, best_value = pso.run()

print("\nBest solution found:", best_position)
print("Best objective value:", round(best_value, 6))