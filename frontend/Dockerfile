# Use the official Node.js image from the Docker Hub
FROM node:16

# Set the working directory in the container
COPY public/ /frontend/public
COPY src/ /frontende/src
COPY package.json /frontend/

# Install the dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Build the application
RUN npm run build

CMD ["npm", "start"]
