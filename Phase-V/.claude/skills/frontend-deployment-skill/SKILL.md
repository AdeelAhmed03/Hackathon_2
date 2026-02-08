---
name: frontend-deployment-skill
description: Deploy static sites, Next.js apps, and frontend applications to CDN and hosting platforms. Use for frontend deployment automation.
---

# Frontend Deployment Skill – Static Sites & Web Applications

## Instructions

1. **Platform-Specific Deployment**
   - **Vercel**: Use `vercel.json` for configuration, environment variables via dashboard or CLI
   - **Netlify**: Configure `netlify.toml`, set up redirects and headers
   - **Cloudflare Pages**: Connect Git repo, configure build settings
   - **AWS S3 + CloudFront**: Set up S3 bucket for static hosting, CloudFront distribution for CDN
   - **GitHub Pages**: Use GitHub Actions to build and deploy to `gh-pages` branch
   - Always test deployments in preview/staging before production

2. **Build Configuration**
   - Define correct build commands (`npm run build`, `next build`, `vite build`)
   - Specify output directory (`.next`, `dist`, `build`, `out`)
   - Configure framework detection or explicitly set framework
   - Optimize build process with caching strategies
   - Set appropriate Node.js version
   - Handle build-time environment variables

3. **Environment Variables**
   - Separate variables by environment (development, preview, production)
   - Prefix public variables correctly (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`)
   - Never commit secrets to version control
   - Use platform-specific secret management
   - Document required environment variables in README

4. **CDN & Caching Strategy**
   - Configure cache headers for static assets (`Cache-Control`)
   - Set immutable cache for versioned assets (JS, CSS with hashes)
   - Use short cache for HTML files to enable quick updates
   - Configure cache invalidation on deployment
   - Enable compression (gzip, brotli)
   - Set up edge caching for global distribution

5. **Custom Domain & SSL**
   - Configure DNS records (A, AAAA, CNAME)
   - Enable automatic SSL certificate provisioning
   - Set up domain redirects (www to non-www or vice versa)
   - Configure subdomain routing if needed
   - Test SSL certificate validity

6. **Preview & Branch Deployments**
   - Enable automatic preview deployments for pull requests
   - Configure branch-specific deployments (staging branch)
   - Set up URL patterns for preview environments
   - Implement deployment comments on PRs
   - Test features in preview before merging

7. **Performance Optimization**
   - Enable image optimization (Next.js Image, Cloudflare Images)
   - Configure asset compression
   - Implement code splitting and lazy loading
   - Set up performance budgets
   - Monitor Core Web Vitals
   - Use edge functions for dynamic content when needed

## Best Practices

- **Immutable Deployments**: Each deployment should be a new immutable version
- **Atomic Deploys**: Ensure all files are updated simultaneously (no partial deploys)
- **Zero Downtime**: Use platforms that support zero-downtime deployments
- **Rollback Ready**: Always have ability to quickly rollback to previous version
- **Preview First**: Test in preview/staging environment before production
- **Monitor Deployments**: Set up alerts for deployment failures
- **Cache Invalidation**: Clear CDN cache after deployments when necessary
- **Security Headers**: Configure security headers (CSP, X-Frame-Options, etc.)

## Example Configurations

### Vercel Deployment

#### vercel.json
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_ANALYTICS_ID": "@analytics-id"
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.example.com/:path*"
    }
  ]
}
```

#### GitHub Actions for Vercel
```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
      
      - name: Pull Vercel Environment Information
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Build Project Artifacts
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Deploy to Vercel
        id: deploy
        run: |
          url=$(vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$url" >> $GITHUB_OUTPUT
      
      - name: Comment PR with deployment URL
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `✅ Deployed to: ${{ steps.deploy.outputs.url }}`
            })
```

### Netlify Deployment

#### netlify.toml
```toml
[build]
  command = "npm run build"
  publish = ".next"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "18"
  NPM_FLAGS = "--legacy-peer-deps"

# Production context
[context.production]
  command = "npm run build"
  
[context.production.environment]
  NEXT_PUBLIC_API_URL = "https://api.example.com"
  NODE_ENV = "production"

# Deploy Preview context (pull requests)
[context.deploy-preview]
  command = "npm run build"
  
[context.deploy-preview.environment]
  NEXT_PUBLIC_API_URL = "https://staging-api.example.com"

# Branch deploy context (staging branch)
[context.staging]
  command = "npm run build"
  
[context.staging.environment]
  NEXT_PUBLIC_API_URL = "https://staging-api.example.com"

# Redirects
[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301

[[redirects]]
  from = "/api/*"
  to = "https://api.example.com/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  conditions = {Role = ["admin"]}

# Headers
[[headers]]
  for = "/*"
  
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"

[[headers]]
  for = "/*.js"
  
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.png"
  
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# Plugin configuration
[[plugins]]
  package = "@netlify/plugin-nextjs"

[[plugins]]
  package = "netlify-plugin-image-optim"
```

### AWS S3 + CloudFront Deployment

#### deploy-to-s3.sh
```bash
#!/bin/bash

set -e

# Configuration
S3_BUCKET="${S3_BUCKET:-my-frontend-bucket}"
CLOUDFRONT_DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID}"
BUILD_DIR="out"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "Building application..."
npm run build

echo "Syncing files to S3..."
aws s3 sync "$BUILD_DIR" "s3://$S3_BUCKET" \
  --region "$AWS_REGION" \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --exclude "service-worker.js"

# Upload HTML files with shorter cache
echo "Uploading HTML files with short cache..."
aws s3 sync "$BUILD_DIR" "s3://$S3_BUCKET" \
  --region "$AWS_REGION" \
  --exclude "*" \
  --include "*.html" \
  --include "service-worker.js" \
  --cache-control "public, max-age=0, must-revalidate"

# Invalidate CloudFront cache
if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
  echo "Invalidating CloudFront cache..."
  aws cloudfront create-invalidation \
    --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
    --paths "/*"
  echo "Cache invalidation initiated"
fi

echo "Deployment complete!"
echo "URL: https://$S3_BUCKET.s3-website-$AWS_REGION.amazonaws.com"
```

#### CloudFormation Template (cloudfront-s3.yaml)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Static website hosting with S3 and CloudFront'

Parameters:
  DomainName:
    Type: String
    Description: Domain name for the website
    Default: example.com
  
  CertificateArn:
    Type: String
    Description: ARN of ACM certificate in us-east-1

Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${DomainName}-frontend'
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: 404.html
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled

  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref S3Bucket
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:GetObject
            Resource: !Sub '${S3Bucket.Arn}/*'
            Condition:
              StringEquals:
                AWS:SourceArn: !Sub 'arn:aws:cloudfront::${AWS::AccountId}:distribution/${CloudFrontDistribution}'

  CloudFrontOriginAccessControl:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub '${DomainName}-oac'
        OriginAccessControlOriginType: s3
        SigningBehavior: always
        SigningProtocol: sigv4

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        HttpVersion: http2and3
        DefaultRootObject: index.html
        Aliases:
          - !Ref DomainName
          - !Sub 'www.${DomainName}'
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt S3Bucket.RegionalDomainName
            OriginAccessControlId: !Ref CloudFrontOriginAccessControl
            S3OriginConfig: {}
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # CachingOptimized
          OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf  # CORS-S3Origin
        CustomErrorResponses:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /index.html
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          SslSupportMethod: sni-only
          MinimumProtocolVersion: TLSv1.2_2021

Outputs:
  BucketName:
    Value: !Ref S3Bucket
    Description: S3 Bucket Name
  
  DistributionId:
    Value: !Ref CloudFrontDistribution
    Description: CloudFront Distribution ID
  
  DistributionDomain:
    Value: !GetAtt CloudFrontDistribution.DomainName
    Description: CloudFront Distribution Domain
  
  WebsiteURL:
    Value: !Sub 'https://${DomainName}'
    Description: Website URL
```

### GitHub Actions for Multiple Platforms
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build application
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: .next
          retention-days: 1

  deploy-vercel:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: .next
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

  deploy-netlify:
    needs: build
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: .next
      
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2
        with:
          publish-dir: '.next'
          production-branch: staging
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: 'Deploy from GitHub Actions'
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}

  deploy-cloudflare:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: .next
      
      - name: Publish to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: my-project
          directory: .next
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

## Performance Optimization Checklist

- [ ] Enable compression (gzip/brotli)
- [ ] Set appropriate cache headers
- [ ] Optimize images (WebP, AVIF formats)
- [ ] Implement code splitting
- [ ] Enable tree shaking
- [ ] Minify JS and CSS
- [ ] Use CDN for static assets
- [ ] Implement lazy loading
- [ ] Set up performance budgets
- [ ] Monitor Core Web Vitals
- [ ] Enable HTTP/2 or HTTP/3
- [ ] Reduce JavaScript bundle size
- [ ] Preload critical resources
- [ ] Use modern image formats

## Troubleshooting Common Issues

**Build Failures:**
- Check Node.js version compatibility
- Verify all environment variables are set
- Clear npm cache: `npm cache clean --force`
- Check build logs for specific errors

**Deployment Not Updating:**
- Verify cache invalidation is working
- Check CDN cache headers
- Ensure atomic deployment completed
- Clear browser cache

**Performance Issues:**
- Analyze bundle size with webpack-bundle-analyzer
- Check Core Web Vitals in Lighthouse
- Verify CDN is serving assets
- Review cache hit ratio

**Domain/SSL Issues:**
- Verify DNS records are correct
- Wait for DNS propagation (up to 48 hours)
- Check SSL certificate status
- Ensure domain is properly verified on platform