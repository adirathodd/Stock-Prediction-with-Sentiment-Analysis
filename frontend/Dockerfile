# Use the official Node.js image from the Docker Hub
FROM node:16

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and yarn.lock files into the container
COPY package.json yarn.lock ./

# Install the dependencies
RUN yarn install

# Copy the rest of the application code into the container
COPY . .

# Build the application
RUN yarn build

# Install a lightweight web server to serve the React application
RUN yarn global add serve

# Specify the command to run on container start
CMD ["serve", "-s", "build"]
