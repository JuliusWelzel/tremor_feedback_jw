function area = SurfArea_st(Z)
%SurfArea Area of interpolated surfaceplot via triangulation
% 
% Author: (Julius Welzel & Mareike Daeglau, University of Oldenburg, 2019)

[m,n] = size(Z);
area = 0;
for i = 1:m-1
      for j = 1:n-1
          v0 = [Xgrid(i,j)     Ygrid(i,j)     Z(i,j)    ];
          v1 = [Xgrid(i,j+1)   Ygrid(i,j+1)   Z(i,j+1)  ];
          v2 = [Xgrid(i+1,j)   Ygrid(i+1,j)   Z(i+1,j)  ];
          v3 = [Xgrid(i+1,j+1) Ygrid(i+1,j+1) Z(i+1,j+1)];
          a = v1 - v0;
          b = v2 - v0;
          c = v3 - v0;
          A = 1/2*(norm(cross(a, c)) + norm(cross(b, c)));
          if isnan(A)
              A = 0;
          end
          area = area + A;
      end
end

end

